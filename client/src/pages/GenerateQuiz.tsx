import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import { Wand2, AlertCircle, Loader2, ArrowRight } from "lucide-react";
import { useGenerateQuiz } from "@/hooks/use-quizzes";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { QuizSummary } from "@/components/QuizSummary";
import { QuestionCard } from "@/components/QuestionCard";
import type { QuizResponse } from "@shared/routes";

const formSchema = z.object({
  url: z.string().url("Please enter a valid URL").refine((val) => val.includes("wikipedia.org"), {
    message: "Must be a Wikipedia URL",
  }),
});

export default function GenerateQuiz() {
  const { mutate, isPending, error } = useGenerateQuiz();
  const [generatedQuiz, setGeneratedQuiz] = useState<QuizResponse | null>(null);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { url: "" },
  });

  const onSubmit = (data: z.infer<typeof formSchema>) => {
    setGeneratedQuiz(null);
    mutate(data, {
      onSuccess: (data) => setGeneratedQuiz(data),
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-12">
      <div className="text-center space-y-4 py-8">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl md:text-6xl font-display font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-600 pb-2"
        >
          Transform Knowledge
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto"
        >
          Paste any Wikipedia article URL to instantly generate an interactive quiz, summary, and entity breakdown.
        </motion.p>
      </div>

      <CardSection>
        <form onSubmit={form.handleSubmit(onSubmit)} className="relative max-w-2xl mx-auto">
          <div className="flex gap-2 p-2 bg-white rounded-2xl shadow-xl shadow-primary/5 border border-primary/10 focus-within:ring-4 focus-within:ring-primary/10 transition-all duration-300">
            <Input
              {...form.register("url")}
              placeholder="https://en.wikipedia.org/wiki/Artificial_intelligence"
              className="flex-1 border-none shadow-none focus-visible:ring-0 text-base md:text-lg h-14 bg-transparent px-4"
              disabled={isPending}
            />
            <Button 
              type="submit" 
              disabled={isPending}
              size="lg"
              className="h-14 px-8 rounded-xl font-semibold bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 transition-all hover:scale-105 active:scale-95"
            >
              {isPending ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5 mr-2" />
                  Generate
                </>
              )}
            </Button>
          </div>
          {form.formState.errors.url && (
            <p className="absolute -bottom-6 left-4 text-sm text-destructive font-medium">
              {form.formState.errors.url.message}
            </p>
          )}
        </form>

        {error && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="max-w-2xl mx-auto mt-6"
          >
            <Alert variant="destructive" className="border-destructive/20 bg-destructive/5">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Generation Failed</AlertTitle>
              <AlertDescription>{error.message}</AlertDescription>
            </Alert>
          </motion.div>
        )}
      </CardSection>

      {generatedQuiz && (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
          <QuizSummary quiz={generatedQuiz} />
          
          <div className="space-y-6">
            <div className="flex items-center gap-2 mb-6">
              <div className="h-8 w-1 bg-primary rounded-full" />
              <h2 className="text-2xl font-display font-bold">Quiz Questions</h2>
              <span className="text-muted-foreground ml-auto text-sm font-medium">
                {generatedQuiz.questions.length} Questions
              </span>
            </div>
            
            <div className="grid gap-6">
              {generatedQuiz.questions.map((question, i) => (
                <QuestionCard key={question.id} question={question} index={i} />
              ))}
            </div>
          </div>

          <div className="flex justify-center pt-8 pb-16">
            <Button variant="outline" size="lg" className="rounded-full gap-2" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
              Generate Another Quiz
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function CardSection({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative z-10">
      {children}
    </div>
  );
}
