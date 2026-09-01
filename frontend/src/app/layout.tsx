import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'GeneRisk — AI-Powered Genomic Risk Intelligence System',
  description:
    'Clinically grounded multi-disease genomic risk assessment, P+T Polygenic Risk Scores, SHAP explainability, and RAG medical guidance.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased selection:bg-brand-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
