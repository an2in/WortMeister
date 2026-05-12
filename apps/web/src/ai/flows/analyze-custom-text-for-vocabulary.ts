'use server';
/**
 * @fileOverview A Genkit flow for analyzing German text, highlighting known and unknown vocabulary.
 *
 * - analyzeCustomTextForVocabulary - A function that handles the text analysis process.
 * - AnalyzeCustomTextForVocabularyInput - The input type for the analyzeCustomTextForVocabulary function.
 * - AnalyzeCustomTextForVocabularyOutput - The return type for the analyzeCustomTextForVocabulary function.
 */

import { ai } from '@/ai/genkit';
import { z } from 'genkit';

const AnalyzeCustomTextForVocabularyInputSchema = z.object({
  germanText: z.string().describe('The German text to be analyzed.'),
  knownVocabulary: z.array(z.string()).describe('An array of German words the user already knows.'),
});
export type AnalyzeCustomTextForVocabularyInput = z.infer<typeof AnalyzeCustomTextForVocabularyInputSchema>;

const AnalyzeCustomTextForVocabularyOutputSchema = z.object({
  knownWordsInText: z.array(z.string()).describe('List of known vocabulary words found in the text.'),
  unknownWordsInText: z.array(
    z.object({
      word: z.string().describe('The unknown German word.'),
      meaning: z.string().describe('A brief English meaning for the unknown word.'),
    })
  ).describe('List of unknown vocabulary words found in the text with their English meanings.'),
});
export type AnalyzeCustomTextForVocabularyOutput = z.infer<typeof AnalyzeCustomTextForVocabularyOutputSchema>;

export async function analyzeCustomTextForVocabulary(input: AnalyzeCustomTextForVocabularyInput): Promise<AnalyzeCustomTextForVocabularyOutput> {
  return analyzeCustomTextForVocabularyFlow(input);
}

const analyzeCustomTextForVocabularyPrompt = ai.definePrompt({
  name: 'analyzeCustomTextForVocabularyPrompt',
  input: { schema: AnalyzeCustomTextForVocabularyInputSchema },
  output: { schema: AnalyzeCustomTextForVocabularyOutputSchema },
  prompt: `You are a German language assistant. Your task is to analyze a given German text and identify words as either 'known' or 'unknown' based on a provided list of known vocabulary.

Instructions:
1. Read the 'germanText' carefully.
2. Go through each significant word (nouns, verbs, adjectives) in the 'germanText'.
3. For each word, check if it exists in the 'knownVocabulary' list.
4. Compile a list of all known words found in the text.
5. Compile a list of all unknown words found in the text. For each unknown word, provide a concise English meaning.
6. Exclude articles (der, die, das, ein, eine, etc.), prepositions (in, auf, an, mit, von, etc.), conjunctions (und, oder, aber, weil, dass, etc.), and pronouns (ich, du, er, sie, es, wir, ihr, sie) from both lists unless they are part of a compound word or phrasal verb that has a specific meaning and is considered a vocabulary item.
7. Return the results in JSON format matching the output schema provided.

German Text: {{{germanText}}}
Known Vocabulary: {{{knownVocabulary}}}`,
});

const analyzeCustomTextForVocabularyFlow = ai.defineFlow(
  {
    name: 'analyzeCustomTextForVocabularyFlow',
    inputSchema: AnalyzeCustomTextForVocabularyInputSchema,
    outputSchema: AnalyzeCustomTextForVocabularyOutputSchema,
  },
  async (input) => {
    const { output } = await analyzeCustomTextForVocabularyPrompt(input);
    if (!output) {
      throw new Error('No output received from the model.');
    }
    return output;
  }
);
