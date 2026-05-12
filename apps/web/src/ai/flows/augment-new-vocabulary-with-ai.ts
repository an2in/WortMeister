'use server';
/**
 * @fileOverview A Genkit flow to augment new German vocabulary with its Part-of-Speech and an illustrative image.
 *
 * - augmentNewVocabularyWithAI - A function that handles the augmentation process.
 * - AugmentNewVocabularyWithAIInput - The input type for the augmentNewVocabularyWithAI function.
 * - AugmentNewVocabularyWithAIOutput - The return type for the augmentNewVocabularyWithAI function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const AugmentNewVocabularyWithAIInputSchema = z.object({
  word: z.string().describe('The German word to augment.'),
});
export type AugmentNewVocabularyWithAIInput = z.infer<typeof AugmentNewVocabularyWithAIInputSchema>;

const AugmentNewVocabularyWithAIOutputSchema = z.object({
  partOfSpeech: z.string().describe('The identified Part-of-Speech of the German word.'),
  imageUrl: z.string().optional().describe('A data URI of an illustrative image for the word, if available.'),
});
export type AugmentNewVocabularyWithAIOutput = z.infer<typeof AugmentNewVocabularyWithAIOutputSchema>;

export async function augmentNewVocabularyWithAI(input: AugmentNewVocabularyWithAIInput): Promise<AugmentNewVocabularyWithAIOutput> {
  return augmentNewVocabularyWithAIFlow(input);
}

const partOfSpeechPrompt = ai.definePrompt({
  name: 'partOfSpeechPrompt',
  input: {schema: AugmentNewVocabularyWithAIInputSchema},
  output: {schema: z.object({ partOfSpeech: z.string() })},
  prompt: `What is the Part-of-Speech (POS) of the German word '{{{word}}}'? Respond with only the POS (e.g., Noun, Verb, Adjective, Adverb, Preposition, Conjunction, Article, Pronoun, Numeral, Interjection). If it can be multiple, pick the most common one.`,
});

const augmentNewVocabularyWithAIFlow = ai.defineFlow(
  {
    name: 'augmentNewVocabularyWithAIFlow',
    inputSchema: AugmentNewVocabularyWithAIInputSchema,
    outputSchema: AugmentNewVocabularyWithAIOutputSchema,
  },
  async (input) => {
    const posResponse = await partOfSpeechPrompt(input);
    const partOfSpeech = posResponse.output?.partOfSpeech || 'Unknown';

    let imageUrl: string | undefined;
    try {
      const imageResponse = await ai.generate({
        model: 'googleai/imagen-4.0-fast-generate-001',
        prompt: `Generate a simple, illustrative image that represents the German word '${input.word}'. The image should be clear and directly related to the meaning of the word.`,
      });
      if (imageResponse.media) {
        imageUrl = imageResponse.media.url;
      }
    } catch (error) {
      console.error(`Failed to generate image for '${input.word}':`, error);
      imageUrl = undefined;
    }

    return {
      partOfSpeech,
      imageUrl,
    };
  }
);
