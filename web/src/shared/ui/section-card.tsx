import { Card, CardProps } from "@mantine/core";
import { PropsWithChildren } from "react";

import { cn } from "@/shared/lib/cn";

type SectionCardProps = PropsWithChildren<CardProps>;

export function SectionCard({ children, className, ...props }: SectionCardProps) {
  return (
    <Card className={cn("panel-surface", className)} {...props}>
      {children}
    </Card>
  );
}
