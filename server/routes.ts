import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";
import * as cheerio from "cheerio";
import OpenAI from "openai";

// Initialize OpenAI client using Replit AI integration env vars
const openai = new OpenAI({
  apiKey: process.env.AI_INTEGRATIONS_OPENAI_API_KEY,
  baseURL: process.env.AI_INTEGRATIONS_OPENAI_BASE_URL,
});

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  app.post(api.quizzes.generate.path, async (req, res) => {
    try {
      const { url } = api.quizzes.generate.input.parse(req.body);

      // 1. Scrape Wikipedia
      const response = await fetch(url);
      if (!response.ok) {
        return res.status(400).json({ message: "Failed to fetch URL" });
      }
      const html = await response.text();
      const $ = cheerio.load(html);
      
      // Extract title and main content
      const title = $("#firstHeading").text().trim();
      // Get content from paragraphs, avoid sidebars/tables for simplicity
      const content = $("#mw-content-text p").map((_, el) => $(el).text()).get().join("\n").slice(0, 15000); // Limit context size

      if (!content) {
         return res.status(400).json({ message: "Could not extract content from the page." });
      }

      // 2. Generate Quiz with LLM
      const prompt = `
        You are a helpful assistant that generates quizzes from Wikipedia articles.
        Based on the following article content about "${title}", generate a quiz.
        
        Article Content (truncated):
        ${content}

        Return a JSON object with the following structure:
        {
          "summary": "A brief summary of the article (2-3 sentences).",
          "key_entities": {
            "people": ["List of key people"],
            "organizations": ["List of key organizations"],
            "locations": ["List of key locations"]
          },
          "sections": ["List of main sections extracted from context if possible, or relevant topics"],
          "related_topics": ["List of 3-5 related Wikipedia topics"],
          "quiz": [
            {
              "question": "Question text",
              "options": ["Option A", "Option B", "Option C", "Option D"],
              "answer": "The correct option text (must be one of the options)",
              "difficulty": "easy" | "medium" | "hard",
              "explanation": "Short explanation of the answer."
            }
          ]
        }
        Generate 5-10 questions. Ensure valid JSON output.
      `;

      const completion = await openai.chat.completions.create({
        model: "gpt-5.2", // Using the recommended model
        messages: [
          { role: "system", content: "You are a JSON generator. output only valid JSON." },
          { role: "user", content: prompt }
        ],
        response_format: { type: "json_object" },
      });

      const result = JSON.parse(completion.choices[0].message.content || "{}");
      
      // Validate result structure roughly (optional but good)
      if (!result.quiz || !Array.isArray(result.quiz)) {
         throw new Error("Invalid LLM response format");
      }

      // 3. Store in DB
      const quizData = {
        url,
        title,
        summary: result.summary || "No summary available.",
        keyEntities: result.key_entities || { people: [], organizations: [], locations: [] },
        sections: result.sections || [],
        relatedTopics: result.related_topics || [],
      };

      const questionsData = result.quiz.map((q: any) => ({
        question: q.question,
        options: q.options,
        answer: q.answer,
        difficulty: q.difficulty || "medium",
        explanation: q.explanation || "",
      }));

      const savedQuiz = await storage.createQuiz(quizData, questionsData);

      res.status(201).json(savedQuiz);
    } catch (err) {
      console.error("Quiz generation error:", err);
      if (err instanceof z.ZodError) {
        return res.status(400).json({
          message: err.errors[0].message,
          field: err.errors[0].path.join('.'),
        });
      }
      res.status(500).json({ message: "Failed to generate quiz." });
    }
  });

  app.get(api.quizzes.list.path, async (req, res) => {
    try {
      const quizzes = await storage.getQuizzes();
      res.json(quizzes);
    } catch (err) {
      res.status(500).json({ message: "Failed to fetch quizzes" });
    }
  });

  app.get(api.quizzes.get.path, async (req, res) => {
    try {
      const quiz = await storage.getQuiz(Number(req.params.id));
      if (!quiz) {
        return res.status(404).json({ message: "Quiz not found" });
      }
      res.json(quiz);
    } catch (err) {
      res.status(500).json({ message: "Failed to fetch quiz" });
    }
  });

  // Seed sample data if empty
  const existing = await storage.getQuizzes();
  if (existing.length === 0) {
    const sampleQuiz = {
      url: "https://en.wikipedia.org/wiki/Alan_Turing",
      title: "Alan Turing",
      summary: "Alan Mathison Turing was an English mathematician, computer scientist, logician, cryptanalyst, philosopher, and theoretical biologist.",
      keyEntities: {
        people: ["Alan Turing", "Alonzo Church"],
        organizations: ["University of Cambridge", "Bletchley Park"],
        locations: ["United Kingdom"]
      },
      sections: ["Early life", "World War II", "Legacy"],
      relatedTopics: ["Cryptography", "Enigma machine", "Computer science history"]
    };
    
    const sampleQuestions = [
      {
        question: "Where did Alan Turing study?",
        options: ["Harvard University", "Cambridge University", "Oxford University", "Princeton University"],
        answer: "Cambridge University",
        difficulty: "easy",
        explanation: "He studied at King's College, Cambridge."
      },
      {
        question: "What was his main contribution during WWII?",
        options: ["Atomic research", "Breaking the Enigma code", "Inventing radar", "Developing jet engines"],
        answer: "Breaking the Enigma code",
        difficulty: "medium",
        explanation: "He worked at Bletchley Park on breaking the Enigma code."
      }
    ];
    
    await storage.createQuiz(sampleQuiz, sampleQuestions);
  }

  return httpServer;
}
