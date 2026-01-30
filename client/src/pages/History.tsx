import { Link } from "wouter";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { Search, Calendar, ChevronRight, BookOpen } from "lucide-react";
import { useQuizzes } from "@/hooks/use-quizzes";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useState } from "react";

export default function History() {
  const { data: quizzes, isLoading, error } = useQuizzes();
  const [search, setSearch] = useState("");

  const filteredQuizzes = quizzes?.filter(q => 
    q.title.toLowerCase().includes(search.toLowerCase()) || 
    q.summary.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold">Quiz History</h1>
          <p className="text-muted-foreground">Review your past generated quizzes</p>
        </div>
        
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search quizzes..." 
            className="pl-9 bg-white"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="grid gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center space-x-4 p-4 border rounded-xl bg-white">
              <Skeleton className="h-12 w-12 rounded-full" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-[250px]" />
                <Skeleton className="h-4 w-[200px]" />
              </div>
            </div>
          ))}
        </div>
      ) : error ? (
        <Card className="bg-destructive/5 border-destructive/20 p-8 text-center">
          <p className="text-destructive font-medium">Failed to load history</p>
        </Card>
      ) : filteredQuizzes?.length === 0 ? (
        <Card className="border-dashed p-12 text-center bg-muted/30">
          <div className="flex flex-col items-center gap-4">
            <div className="p-4 bg-muted rounded-full">
              <BookOpen className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold">No quizzes found</h3>
            <p className="text-muted-foreground max-w-sm mx-auto">
              You haven't generated any quizzes yet. Go to the Generate tab to create your first one!
            </p>
            <Link href="/">
              <a className="text-primary hover:underline font-medium mt-2 inline-block">
                Create Quiz
              </a>
            </Link>
          </div>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredQuizzes?.map((quiz, i) => (
            <motion.div
              key={quiz.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link href={`/quiz/${quiz.id}`}>
                <div className="group block bg-white hover:bg-accent/50 border border-border/50 hover:border-primary/20 rounded-xl p-5 transition-all duration-200 shadow-sm hover:shadow-md cursor-pointer">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="font-display font-semibold text-lg text-foreground truncate group-hover:text-primary transition-colors">
                          {quiz.title}
                        </h3>
                        <Badge variant="secondary" className="text-xs shrink-0 bg-primary/5 text-primary">
                          {format(new Date(quiz.createdAt), 'MMM d, yyyy')}
                        </Badge>
                      </div>
                      <p className="text-muted-foreground text-sm line-clamp-2 leading-relaxed">
                        {quiz.summary}
                      </p>
                      
                      <div className="flex items-center gap-4 mt-4 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5" />
                          {format(new Date(quiz.createdAt), 'h:mm a')}
                        </div>
                        <div className="flex gap-1">
                          {quiz.keyEntities.people.slice(0, 3).map((person, j) => (
                            <span key={j} className="bg-muted px-1.5 py-0.5 rounded text-muted-foreground/80">
                              {person}
                            </span>
                          ))}
                          {quiz.keyEntities.people.length > 3 && (
                            <span className="bg-muted px-1.5 py-0.5 rounded">+{quiz.keyEntities.people.length - 3}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="self-center">
                      <div className="w-10 h-10 rounded-full bg-muted/50 group-hover:bg-primary/10 flex items-center justify-center transition-colors">
                        <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary" />
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
