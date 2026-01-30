import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, buildUrl, type GenerateQuizInput, type QuizResponse, type QuizListResponse } from "@shared/routes";
import { useToast } from "@/hooks/use-toast";
import { config } from "@/lib/apiConfig";

// GET /api/quizzes
export function useQuizzes() {
  return useQuery<QuizListResponse[]>({
    queryKey: [api.quizzes.list.path],
    queryFn: async () => {
      const url = `${config.apiBaseUrl}${api.quizzes.list.path}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to fetch quizzes");
      return await res.json();
    },
  });
}

// GET /api/quizzes/:id
export function useQuiz(id: number) {
  return useQuery<QuizResponse>({
    queryKey: [api.quizzes.get.path, id],
    enabled: !!id,
    queryFn: async () => {
      const url = `${config.apiBaseUrl}${api.quizzes.get.path.replace(':id', String(id))}`;
      const res = await fetch(url);
      if (res.status === 404) throw new Error("Quiz not found");
      if (!res.ok) throw new Error("Failed to fetch quiz details");
      return await res.json();
    },
  });
}

// POST /api/quizzes/generate
export function useGenerateQuiz() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (data: GenerateQuizInput) => {
      const url = `${config.apiBaseUrl}${api.quizzes.generate.path}`;
      const res = await fetch(url, {
        method: api.quizzes.generate.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Failed to generate quiz" }));
        throw new Error(error.detail || error.message || "Failed to generate quiz");
      }
      return await res.json();
    },
    onSuccess: (data: QuizResponse) => {
      queryClient.invalidateQueries({ queryKey: [api.quizzes.list.path] });
      toast({
        title: "Quiz Generated!",
        description: `Successfully created quiz for "${data.title}"`,
      });
    },
    onError: (error: Error) => {
      toast({
        variant: "destructive",
        title: "Generation Failed",
        description: error.message,
      });
    },
  });
}
