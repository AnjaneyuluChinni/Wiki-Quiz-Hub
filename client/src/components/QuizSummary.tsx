import { motion } from "framer-motion";
import { Users, Building2, MapPin, Hash, Sparkles } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Quiz } from "@shared/schema";

interface QuizSummaryProps {
  quiz: Quiz;
}

export function QuizSummary({ quiz }: QuizSummaryProps) {
  const entities = [
    { label: "People", icon: Users, items: quiz.keyEntities.people, color: "bg-blue-100 text-blue-700 hover:bg-blue-200" },
    { label: "Organizations", icon: Building2, items: quiz.keyEntities.organizations, color: "bg-purple-100 text-purple-700 hover:bg-purple-200" },
    { label: "Locations", icon: MapPin, items: quiz.keyEntities.locations, color: "bg-amber-100 text-amber-700 hover:bg-amber-200" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="mb-8"
    >
      <Card className="bg-white/50 backdrop-blur-sm border-primary/10 shadow-xl overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl -mr-16 -mt-16" />
        
        <CardHeader className="relative border-b border-border/50 pb-8">
          <div className="flex items-center gap-2 text-primary text-sm font-bold uppercase tracking-wider mb-2">
            <Sparkles className="w-4 h-4" />
            <span>Quiz Summary</span>
          </div>
          <CardTitle className="text-3xl md:text-4xl font-display font-bold text-foreground mb-4">
            {quiz.title}
          </CardTitle>
          <p className="text-lg text-muted-foreground leading-relaxed max-w-3xl">
            {quiz.summary}
          </p>
        </CardHeader>
        
        <CardContent className="pt-8 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {entities.map((section) => (
            section.items.length > 0 && (
              <div key={section.label} className="space-y-3">
                <div className="flex items-center gap-2 text-muted-foreground font-medium">
                  <section.icon className="w-4 h-4" />
                  {section.label}
                </div>
                <div className="flex flex-wrap gap-2">
                  {section.items.map((item, i) => (
                    <Badge 
                      key={i} 
                      variant="secondary"
                      className={`transition-colors ${section.color} border-transparent`}
                    >
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
            )
          ))}

          {quiz.relatedTopics.length > 0 && (
            <div className="space-y-3 md:col-span-2 lg:col-span-3">
              <div className="flex items-center gap-2 text-muted-foreground font-medium">
                <Hash className="w-4 h-4" />
                Related Topics
              </div>
              <div className="flex flex-wrap gap-2">
                {quiz.relatedTopics.map((topic, i) => (
                  <Badge key={i} variant="outline" className="border-primary/20 hover:border-primary/50 text-foreground/80">
                    {topic}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
