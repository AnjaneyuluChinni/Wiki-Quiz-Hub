import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, ChevronDown, ChevronUp } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Question } from "@shared/schema";

interface QuestionCardProps {
  question: Question;
  index: number;
}

export function QuestionCard({ question, index }: QuestionCardProps) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  
  const isCorrect = selectedOption === question.answer;
  const hasAnswered = selectedOption !== null;

  const difficultyColors = {
    easy: "bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800",
    medium: "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800",
    hard: "bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      <Card className="overflow-hidden border-border/50 shadow-md hover:shadow-lg transition-all duration-300">
        <div className="p-6">
          <div className="flex justify-between items-start mb-4 gap-4">
            <h3 className="text-lg font-semibold font-display text-foreground leading-relaxed">
              <span className="text-muted-foreground mr-2 opacity-50">#{index + 1}</span>
              {question.question}
            </h3>
            <Badge 
              variant="outline" 
              className={cn("capitalize shrink-0", difficultyColors[question.difficulty as keyof typeof difficultyColors])}
            >
              {question.difficulty}
            </Badge>
          </div>

          <div className="grid gap-3">
            {question.options.map((option, optIndex) => {
              const isSelected = selectedOption === option;
              const isAnswer = option === question.answer;
              
              let stateStyles = "hover:bg-accent hover:border-accent-foreground/20";
              
              if (hasAnswered) {
                if (isAnswer) stateStyles = "bg-green-50 border-green-200 ring-1 ring-green-500 dark:bg-green-900/20 dark:border-green-800";
                else if (isSelected && !isAnswer) stateStyles = "bg-red-50 border-red-200 ring-1 ring-red-500 dark:bg-red-900/20 dark:border-red-800";
                else stateStyles = "opacity-50 grayscale";
              } else if (isSelected) {
                stateStyles = "bg-primary/5 border-primary ring-1 ring-primary";
              }

              return (
                <button
                  key={optIndex}
                  onClick={() => !hasAnswered && setSelectedOption(option)}
                  disabled={hasAnswered}
                  className={cn(
                    "w-full text-left p-4 rounded-xl border-2 transition-all duration-200 flex items-center justify-between group",
                    stateStyles
                  )}
                >
                  <span className="font-medium text-sm md:text-base">{option}</span>
                  {hasAnswered && isAnswer && <CheckCircle2 className="w-5 h-5 text-green-600" />}
                  {hasAnswered && isSelected && !isAnswer && <XCircle className="w-5 h-5 text-red-600" />}
                </button>
              );
            })}
          </div>

          <AnimatePresence>
            {hasAnswered && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6"
              >
                <div className={cn(
                  "rounded-xl p-4 border",
                  isCorrect 
                    ? "bg-green-50/50 border-green-100 dark:bg-green-900/10 dark:border-green-900/50" 
                    : "bg-blue-50/50 border-blue-100 dark:bg-blue-900/10 dark:border-blue-900/50"
                )}>
                  <div className="flex items-center gap-2 mb-2">
                    <HelpCircle className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Explanation</span>
                  </div>
                  <p className="text-sm text-foreground/80 leading-relaxed">
                    {question.explanation}
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </Card>
    </motion.div>
  );
}
