import { config } from 'dotenv';
config();

import '@/ai/flows/generate-custom-pronunciation-flow.ts';
import '@/ai/flows/analyze-custom-text-for-vocabulary.ts';
import '@/ai/flows/augment-new-vocabulary-with-ai.ts';