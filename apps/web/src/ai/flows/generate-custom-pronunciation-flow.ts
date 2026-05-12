'use server';
/**
 * @fileOverview A Genkit flow for generating custom audio pronunciations for German text.
 *
 * - generateCustomPronunciation - A function that handles the text-to-speech conversion process.
 * - GenerateCustomPronunciationInput - The input type for the generateCustomPronunciation function.
 * - GenerateCustomPronunciationOutput - The return type for the generateCustomPronunciation function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';
import {googleAI} from '@genkit-ai/google-genai';
import wav from 'wav';
import {Readable} from 'stream';

const GenerateCustomPronunciationInputSchema = z.object({
  text: z.string().describe('The German text (word, phrase, or sentence) to be pronounced.'),
});
export type GenerateCustomPronunciationInput = z.infer<typeof GenerateCustomPronunciationInputSchema>;

const GenerateCustomPronunciationOutputSchema = z.object({
  media: z.string().describe('The base64 encoded audio in WAV format, as a data URI.'),
});
export type GenerateCustomPronunciationOutput = z.infer<typeof GenerateCustomPronunciationOutputSchema>;

export async function generateCustomPronunciation(input: GenerateCustomPronunciationInput): Promise<GenerateCustomPronunciationOutput> {
  return generateCustomPronunciationFlow(input);
}

const generateCustomPronunciationFlow = ai.defineFlow(
  {
    name: 'generateCustomPronunciationFlow',
    inputSchema: GenerateCustomPronunciationInputSchema,
    outputSchema: GenerateCustomPronunciationOutputSchema,
  },
  async (input) => {
    const { media } = await ai.generate({
      model: googleAI.model('gemini-2.5-flash-preview-tts'),
      config: {
        responseModalities: ['AUDIO'],
        speechConfig: {
          voiceConfig: {
            prebuiltVoiceConfig: { voiceName: 'Algenib' },
          },
        },
      },
      prompt: input.text,
    });

    if (!media) {
      throw new Error('No audio media returned from TTS model.');
    }

    const audioBuffer = Buffer.from(
      media.url.substring(media.url.indexOf(',') + 1),
      'base64'
    );

    const wavBase64 = await toWav(audioBuffer);

    return {
      media: 'data:audio/wav;base64,' + wavBase64,
    };
  }
);

// Helper function to convert PCM audio buffer to WAV format
async function toWav(
  pcmData: Buffer,
  channels = 1,
  rate = 24000,
  sampleWidth = 2
): Promise<string> {
  return new Promise((resolve, reject) => {
    const writer = new wav.Writer({
      channels,
      sampleRate: rate,
      bitDepth: sampleWidth * 8,
    });

    const bufs: any[] = [];
    writer.on('error', reject);
    writer.on('data', function (d) {
      bufs.push(d);
    });
    writer.on('end', function () {
      resolve(Buffer.concat(bufs).toString('base64'));
    });

    // Create a readable stream from the PCM data and pipe it to the WAV writer
    const pcmStream = new Readable();
    pcmStream.push(pcmData);
    pcmStream.push(null); // Indicate end of stream
    pcmStream.pipe(writer);
  });
}
