export interface TextFragment {
  type: 'text' | 'mention';
  value: string;       // displayed text (for mentions includes leading '@')
  username?: string;   // username without '@', set for mentions only
}

const MENTION_RE = /@([A-Za-z0-9_]{1,150})/g;

/**
 * Splits free-form text into plain and @mention fragments.
 * Renders safely as routerLinks without using innerHTML.
 */
export function splitMentions(text: string): TextFragment[] {
  if (!text) return [];
  const out: TextFragment[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  MENTION_RE.lastIndex = 0;
  while ((m = MENTION_RE.exec(text)) !== null) {
    if (m.index > last) {
      out.push({ type: 'text', value: text.slice(last, m.index) });
    }
    out.push({ type: 'mention', value: m[0], username: m[1] });
    last = m.index + m[0].length;
  }
  if (last < text.length) {
    out.push({ type: 'text', value: text.slice(last) });
  }
  return out;
}
