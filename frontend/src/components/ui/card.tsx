// Simple Card components for the chat interface
import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
}

interface CardHeaderProps {
  children: ReactNode;
}

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

interface CardContentProps {
  children: ReactNode;
}

export function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      {children}
    </div>
  );
}

export function CardHeader({ children }: CardHeaderProps) {
  return (
    <div className="px-6 py-4 border-b border-gray-200">
      {children}
    </div>
  );
}

export function CardTitle({ children, className = '' }: CardTitleProps) {
  return (
    <h3 className={`text-lg font-semibold text-gray-900 ${className}`}>
      {children}
    </h3>
  );
}

export function CardContent({ children }: CardContentProps) {
  return (
    <div className="px-6 py-4">
      {children}
    </div>
  );
}