import { buildPhoto } from './photo.js';
import { buildCampaign } from './campaign.js';
import { buildBenefits } from './benefits.js';
import { buildFinale } from './finale.js';

/** Modèles de scènes. Pour en ajouter un : créer le fichier, puis l'inscrire ici. */
export const TEMPLATES = { photo: buildPhoto, campaign: buildCampaign, benefits: buildBenefits, finale: buildFinale };
