import { db } from "./db";
import {
  quizzes,
  questions,
  type Quiz,
  type Question,
  type InsertQuiz,
  type InsertQuestion,
  type QuizWithQuestions
} from "@shared/schema";
import { eq, desc } from "drizzle-orm";

export interface IStorage {
  createQuiz(quiz: InsertQuiz, questionsData: InsertQuestion[]): Promise<QuizWithQuestions>;
  getQuizzes(): Promise<Quiz[]>;
  getQuiz(id: number): Promise<QuizWithQuestions | undefined>;
}

export class DatabaseStorage implements IStorage {
  async createQuiz(quizData: InsertQuiz, questionsData: InsertQuestion[]): Promise<QuizWithQuestions> {
    const result = await db.transaction(async (tx) => {
      const [quiz] = await tx.insert(quizzes).values(quizData).returning();
      
      const questionsWithQuizId = questionsData.map(q => ({
        ...q,
        quizId: quiz.id,
      }));
      
      const insertedQuestions = await tx.insert(questions).values(questionsWithQuizId).returning();
      
      return {
        ...quiz,
        questions: insertedQuestions,
      };
    });
    return result;
  }

  async getQuizzes(): Promise<Quiz[]> {
    return await db.select().from(quizzes).orderBy(desc(quizzes.createdAt));
  }

  async getQuiz(id: number): Promise<QuizWithQuestions | undefined> {
    const [quiz] = await db.select().from(quizzes).where(eq(quizzes.id, id));
    if (!quiz) return undefined;

    const quizQuestions = await db.select().from(questions).where(eq(questions.quizId, id));
    
    return {
      ...quiz,
      questions: quizQuestions,
    };
  }
}

export const storage = new DatabaseStorage();
