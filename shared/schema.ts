import { pgTable, text, serial, timestamp, jsonb, integer } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";
import { relations } from "drizzle-orm";

export const quizzes = pgTable("quizzes", {
  id: serial("id").primaryKey(),
  url: text("url").notNull(),
  title: text("title").notNull(),
  summary: text("summary").notNull(),
  keyEntities: jsonb("key_entities").$type<{
    people: string[];
    organizations: string[];
    locations: string[];
  }>().notNull(),
  sections: jsonb("sections").$type<string[]>().notNull(),
  relatedTopics: jsonb("related_topics").$type<string[]>().notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const questions = pgTable("questions", {
  id: serial("id").primaryKey(),
  quizId: integer("quiz_id").notNull(),
  question: text("question").notNull(),
  options: jsonb("options").$type<string[]>().notNull(),
  answer: text("answer").notNull(),
  difficulty: text("difficulty").notNull(), // "easy", "medium", "hard"
  explanation: text("explanation").notNull(),
});

export const quizzesRelations = relations(quizzes, ({ many }) => ({
  questions: many(questions),
}));

export const questionsRelations = relations(questions, ({ one }) => ({
  quiz: one(quizzes, {
    fields: [questions.quizId],
    references: [quizzes.id],
  }),
}));

export const insertQuizSchema = createInsertSchema(quizzes).omit({ id: true, createdAt: true });
export const insertQuestionSchema = createInsertSchema(questions).omit({ id: true });

export type Quiz = typeof quizzes.$inferSelect;
export type Question = typeof questions.$inferSelect;
export type InsertQuiz = z.infer<typeof insertQuizSchema>;
export type InsertQuestion = z.infer<typeof insertQuestionSchema>;

// Combined type for API response
export type QuizWithQuestions = Quiz & { questions: Question[] };
