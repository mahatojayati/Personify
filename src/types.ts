export interface SpotifyArtist {
  name: string;
  genres: string[];
  popularity?: number;
  imageUrl?: string;
}

export interface SpotifyTrack {
  name: string;
  artist: string;
  albumArt?: string;
}

export interface MusicalFinding {
  id?: number | string;
  source: 'spotify_connect' | 'spotify_artists' | 'spotify_search' | 'spotify_preset';
  identifier: string; // Username, Artist names, or Playlist/Profile title
  genres_analyzed: string[];
  top_artists?: string[];
  top_tracks?: string[];
  ocean_scores?: {
    openness: number;
    conscientiousness: number;
    extraversion: number;
    agreeableness: number;
    neuroticism: number;
  };
  archetype?: string;
  ocean_report: string;
  created_at?: string;
}

export interface AnalysisResponse {
  success: boolean;
  source?: string;
  identifier: string;
  genres_analyzed: string[];
  top_artists?: string[];
  top_tracks?: string[];
  ocean_scores?: {
    openness: number;
    conscientiousness: number;
    extraversion: number;
    agreeableness: number;
    neuroticism: number;
  };
  archetype?: string;
  ocean_report: string;
  error?: string;
}

export interface SpotifyAuthStatus {
  authenticated: boolean;
  spotifyUser?: {
    id: string;
    display_name: string;
    images?: Array<{ url: string }>;
    product?: string;
  };
  hasCredentials: boolean;
}
