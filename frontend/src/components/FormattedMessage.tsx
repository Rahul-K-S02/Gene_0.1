'use client';

import React from 'react';

interface FormattedMessageProps {
  content: string;
  className?: string;
  isUser?: boolean;
}

function renderInlineText(text: string, isUser = false): React.ReactNode {
  const clean = text
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<\/?[a-z][a-z0-9]*[^<>]*>/gi, '');

  const tokens = clean.split(/(\*\*.*?\*\*|`.*?`|\*.*?\*)/g);

  return tokens.map((tok, i) => {
    if (tok.startsWith('**') && tok.endsWith('**') && tok.length >= 4) {
      return (
        <strong key={i} className={`font-bold ${isUser ? 'text-white' : 'text-slate-900'}`}>
          {tok.slice(2, -2)}
        </strong>
      );
    }
    if (tok.startsWith('`') && tok.endsWith('`') && tok.length >= 2) {
      return (
        <code
          key={i}
          className={`rounded px-1 py-0.5 font-mono text-[11px] ${
            isUser ? 'bg-brand-700 text-white' : 'bg-slate-100 text-slate-800'
          }`}
        >
          {tok.slice(1, -1)}
        </code>
      );
    }
    if (tok.startsWith('*') && tok.endsWith('*') && tok.length >= 2) {
      return (
        <em key={i} className="italic">
          {tok.slice(1, -1)}
        </em>
      );
    }
    return tok;
  });
}

export const FormattedMessage: React.FC<FormattedMessageProps> = ({
  content,
  className = '',
  isUser = false,
}) => {
  if (!content) return null;

  if (isUser) {
    return <p className={`whitespace-pre-wrap ${className}`}>{content}</p>;
  }

  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];

  let currentList: { type: 'ul' | 'ol'; items: string[] } | null = null;
  let currentTable: string[] | null = null;

  const flushList = () => {
    if (currentList) {
      if (currentList.type === 'ul') {
        elements.push(
          <ul key={`ul-${elements.length}`} className="my-2 space-y-1 pl-4 list-disc marker:text-brand-500">
            {currentList.items.map((item, idx) => (
              <li key={idx} className="leading-relaxed">
                {renderInlineText(item, isUser)}
              </li>
            ))}
          </ul>
        );
      } else {
        elements.push(
          <ol key={`ol-${elements.length}`} className="my-2 space-y-1 pl-4 list-decimal marker:font-bold marker:text-slate-600">
            {currentList.items.map((item, idx) => (
              <li key={idx} className="leading-relaxed">
                {renderInlineText(item, isUser)}
              </li>
            ))}
          </ol>
        );
      }
      currentList = null;
    }
  };

  const flushTable = () => {
    if (currentTable && currentTable.length > 0) {
      const rows = currentTable
        .map((r) =>
          r
            .split('|')
            .map((c) => c.trim())
            .filter((c, idx, arr) => (idx > 0 && idx < arr.length - 1) || arr.length <= 2)
        )
        .filter((cells) => cells.length > 0 && !cells.every((c) => /^:?-+:?$/.test(c)));

      if (rows.length > 0) {
        const headerRow = rows[0];
        const bodyRows = rows.slice(1);

        elements.push(
          <div key={`table-${elements.length}`} className="my-3 overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-2xs">
            <table className="w-full text-left text-[11px]">
              <thead className="bg-slate-100/90 border-b border-slate-200 text-slate-800 font-bold">
                <tr>
                  {headerRow.map((h, i) => (
                    <th key={i} className="px-3 py-2">
                      {renderInlineText(h, isUser)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {bodyRows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-slate-50/70 transition-colors">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="px-3 py-2 text-slate-700 align-top">
                        {renderInlineText(cell, isUser)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
      currentTable = null;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    if (trimmed.startsWith('|') && trimmed.endsWith('|') && trimmed.includes('|')) {
      flushList();
      if (!currentTable) currentTable = [];
      currentTable.push(trimmed);
      continue;
    } else if (currentTable) {
      flushTable();
    }

    if (/^[-*_]{3,}$/.test(trimmed)) {
      flushList();
      elements.push(<hr key={`hr-${elements.length}`} className="my-2.5 border-slate-200" />);
      continue;
    }

    if (/^#{1,4}\s+/.test(trimmed)) {
      flushList();
      const level = trimmed.match(/^#+/)?.[0].length || 1;
      const text = trimmed.replace(/^#+\s+/, '');
      if (level <= 2) {
        elements.push(
          <h4 key={`h-${elements.length}`} className="mt-3 mb-1 text-sm font-bold text-slate-900 flex items-center gap-1.5">
            {renderInlineText(text, isUser)}
          </h4>
        );
      } else {
        elements.push(
          <h5 key={`h-${elements.length}`} className="mt-2.5 mb-1 text-xs font-bold text-slate-800 uppercase tracking-wide">
            {renderInlineText(text, isUser)}
          </h5>
        );
      }
      continue;
    }

    if (/^[-*•]\s+/.test(trimmed)) {
      const itemText = trimmed.replace(/^[-*•]\s+/, '');
      if (!currentList || currentList.type !== 'ul') {
        flushList();
        currentList = { type: 'ul', items: [] };
      }
      currentList.items.push(itemText);
      continue;
    }

    if (/^\d+[.)]\s+/.test(trimmed)) {
      const itemText = trimmed.replace(/^\d+[.)]\s+/, '');
      if (!currentList || currentList.type !== 'ol') {
        flushList();
        currentList = { type: 'ol', items: [] };
      }
      currentList.items.push(itemText);
      continue;
    }

    if (!trimmed) {
      flushList();
      continue;
    }

    flushList();
    elements.push(
      <p key={`p-${elements.length}`} className="my-1 leading-relaxed">
        {renderInlineText(trimmed, isUser)}
      </p>
    );
  }

  flushList();
  flushTable();

  return <div className={`space-y-1 text-xs text-slate-800 leading-relaxed ${className}`}>{elements}</div>;
};
