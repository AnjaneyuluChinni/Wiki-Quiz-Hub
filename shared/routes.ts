import { z } from 'zod';
import { insertQuizSchema, quizzes, questions } from './schema';

export const errorSchemas = {
  validation: z.object({
    message: z.string(),
    field: z.string().optional(),
  }),
  notFound: z.object({
    message: z.string(),
  }),
  internal: z.object({
    message: z.string(),
  }),
};

export const api = {
  quizzes: {
    generate: {
      method: 'POST' as const,
      path: '/api/quizzes/generate',
      input: z.object({
        url: z.string().url(),
      }),
      responses: {
        201: z.custom<Quiz & { questions: Question[] }>(),
        400: errorSchemas.validation,
        500: errorSchemas.internal,
      },
    },
    list: {
      method: 'GET' as const,
      path: '/api/quizzes',
      responses: {
        200: z.array(z.custom<Quiz>()),
      },
    },
    get: {
      method: 'GET' as const,
      path: '/api/quizzes/:id',
      responses: {
        200: z.custom<Quiz & { questions: Question[] }>(),
        404: errorSchemas.notFound,
      },
    },
  },
};

export function buildUrl(path: string, params?: Record<string, string | number>): string {
  let url = path;
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (url.includes(`:${key}`)) {
        url = url.replace(`:${key}`, String(value));
      }
    });
  }
  return url;
}

// Type definitions
export type GenerateQuizInput = z.infer<typeof api.quizzes.generate.input>;
export type QuizResponse = z.infer<typeof api.quizzes.generate.responses[201]>;
export type QuizListResponse = z.infer<typeof api.quizzes.list.responses[200]>;
