import { useRoute, Link } from "wouter";
import { ArrowLeft, Loader2 } from "lucide-react";
import { useQuiz } from "@/hooks/use-quizzes";
import { Button } from "@/components/ui/button";
import { QuizSummary } from "@/components/QuizSummary";
import { QuestionCard } from "@/components/QuestionCard";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";

export default function QuizDetail() {
  const [, params] = useRoute("/quiz/:id");
  const id = params ? parseInt(params.id) : 0;
  const { data: quiz, isLoading, error } = useQuiz(id);

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
        <p className="text-muted-foreground font-medium">Loading quiz...</p>
      </div>
    );
  }

  if (error || !quiz) {
    return (
      <div className="max-w-2xl mx-auto mt-12">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error?.message || "Quiz not found"}</AlertDescription>
        </Alert>
        <Button className="mt-4" variant="outline" asChild>
          <Link href="/history">Back to History</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto pb-16">
      <div className="mb-8">
        <Link href="/history">
          <a className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-primary transition-colors mb-4">
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to History
          </a>
        </Link>
      </div>

      <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
        <QuizSummary quiz={quiz} />
        
        <div className="space-y-6 mt-12">
          <div className="flex items-center gap-2 mb-6">
            <div className="h-8 w-1 bg-primary rounded-full" />
            <h2 className="text-2xl font-display font-bold">Quiz Questions</h2>
          </div>
          
          <div className="grid gap-6">
            {quiz.questions.map((question, i) => (
              <QuestionCard key={question.id} question={question} index={i} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
