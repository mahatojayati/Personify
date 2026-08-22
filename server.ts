import express from "express";
import cors from "cors";
import path from "path";
import axios from "axios";
import { GoogleGenAI } from "@google/genai";
import { createServer as createViteServer } from "vite";

interface Finding {
  id: number | string;
  source: 'spotify_connect' | 'spotify_artists' | 'spotify_search' | 'spotify_preset';
  identifier: string;
  genres_analyzed: string[];
  top_artists?: string[];
  top_tracks?: string[];
  ocean_scores: {
    openness: number;
    conscientiousness: number;
    extraversion: number;
    agreeableness: number;
    neuroticism: number;
  };
  archetype: string;
  ocean_report: string;
  created_at: string;
}

// In-memory store initialized with seed Spotify musical profiles
const findingsStore: Finding[] = [
  {
    id: 1,
    source: "spotify_artists",
    identifier: "Radiohead, Tame Impala, Beach House, Tycho",
    genres_analyzed: ["art rock", "psychedelic pop", "dream pop", "ambient", "indie rock", "chillwave", "shoegaze"],
    top_artists: ["Radiohead", "Tame Impala", "Beach House", "Tycho"],
    top_tracks: ["Weird Fishes / Arpeggi", "Let It Happen", "Space Song", "Awake"],
    ocean_scores: {
      openness: 94,
      conscientiousness: 62,
      extraversion: 38,
      agreeableness: 76,
      neuroticism: 55,
    },
    archetype: "The Atmospheric Architect",
    ocean_report: `### 🧠 Psychological Profile: Big Five (OCEAN) Framework

#### **Dominant Traits**
* **Openness to Experience (94% - Exceptionally High)**: A clear preference for layered sonic landscapes, non-traditional time signatures, and atmospheric synthesis. Reflects heightened aesthetic sensitivity, deep intellectual curiosity, and an appetite for cognitive abstraction.
* **Conscientiousness (62% - Moderate-High)**: Demonstrates sustained cognitive focus and attention span, aligning with extended track structures and immersive album-oriented listening styles.
* **Extraversion (38% - Low-Moderate / Introspective)**: Listening habits indicate internal cognitive reflection and solitary mood calibration rather than social background stimulus.
* **Agreeableness (76% - High)**: High emotional empathy and receptivity to poignant melodic narratives and vulnerable vocal timbres.
* **Neuroticism / Emotional Receptivity (55% - Balanced Resilience)**: Utilizes music as a safe, structured conduit for cathartic emotional processing and creative decompression.

---

#### **Emotional Regulation Style**
* **Contemplative & Aesthetic Rumination**: You leverage rich, spacious textures to carve out mental focus spaces. Listening functions as a cognitive sanctuary for problem solving and quiet creativity.

---

#### **Suggested Activity & Prescription**
* **Immersive Creative Session**: Spend 45 minutes in a low-lit room with high-fidelity headphones, sketching, journaling, or conceptualizing a creative project without verbal distractions.`,
    created_at: new Date(Date.now() - 3600000 * 4).toISOString(),
  },
  {
    id: 2,
    source: "spotify_preset",
    identifier: "Dua Lipa, The Weeknd, Daft Punk, Calvin Harris",
    genres_analyzed: ["dance pop", "synthwave", "electropop", "nu-disco", "house", "french touch"],
    top_artists: ["Dua Lipa", "The Weeknd", "Daft Punk", "Calvin Harris"],
    top_tracks: ["Levitating", "Blinding Lights", "Get Lucky", "One Kiss"],
    ocean_scores: {
      openness: 68,
      conscientiousness: 82,
      extraversion: 88,
      agreeableness: 80,
      neuroticism: 32,
    },
    archetype: "The Rhythmic Catalyst",
    ocean_report: `### 🧠 Psychological Profile: Big Five (OCEAN) Framework

#### **Dominant Traits**
* **Extraversion (88% - Very High)**: Strong attraction to driving four-on-the-floor rhythms, vibrant synth hooks, and high-energy BPMs. Reflects enthusiasm, assertiveness, and outward-facing vitality.
* **Conscientiousness (82% - High)**: Paced, structured rhythmic preferences that mirror goal-driven routines, energetic workouts, and productive pacing.
* **Agreeableness (80% - High)**: Prosocial warmth and natural affinity for universally shared communal energy and feel-good vocal hooks.
* **Openness to Experience (68% - Moderate-High)**: Appreciates modern hybrid production, retro-futuristic synth arrangements, and polished sound design.
* **Emotional Stability (Neuroticism: 32% - Very Low)**: Uses upbeat music as an intentional mood amplifier to sustain high momentum and positive emotional states.

---

#### **Emotional Regulation Style**
* **Energizing & Social Amplification**: Music serves as an auditory espresso shot—catalyzing motivation, driving physical movement, and elevating baseline optimism.

---

#### **Suggested Activity & Prescription**
* **Dynamic Movement or Social Playlist**: Channel this rhythmic drive into a high-energy workout, cycling sprint, or collaborate on an upbeat weekend playlist with friends.`,
    created_at: new Date(Date.now() - 3600000 * 18).toISOString(),
  },
];

// Lazy Gemini API Client
let geminiClient: GoogleGenAI | null = null;
function getGemini(): GoogleGenAI {
  const key = process.env.GEMINI_API_KEY;
  if (!key) {
    throw new Error("GEMINI_API_KEY is not configured in environment variables.");
  }
  if (!geminiClient) {
    geminiClient = new GoogleGenAI({ apiKey: key });
  }
  return geminiClient;
}

// Spotify Client Credentials Token Cache
let spotifyAppToken: { token: string; expiresAt: number } | null = null;

async function getSpotifyAppToken(): Promise<string | null> {
  const clientId = process.env.SPOTIFY_CLIENT_ID;
  const clientSecret = process.env.SPOTIFY_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    return null;
  }

  if (spotifyAppToken && Date.now() < spotifyAppToken.expiresAt) {
    return spotifyAppToken.token;
  }

  try {
    const authHeader = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");
    const response = await axios.post(
      "https://accounts.spotify.com/api/token",
      new URLSearchParams({ grant_type: "client_credentials" }).toString(),
      {
        headers: {
          Authorization: `Basic ${authHeader}`,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout: 6000,
      }
    );

    const token = response.data?.access_token;
    const expiresIn = response.data?.expires_in || 3600;
    if (token) {
      spotifyAppToken = {
        token,
        expiresAt: Date.now() + (expiresIn - 60) * 1000,
      };
      return token;
    }
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.warn("Spotify Client Credentials authentication failed:", msg);
  }
  return null;
}

// Fetch artist data and genres from Spotify Web API
async function fetchSpotifyArtistDetails(artistQuery: string): Promise<{ artists: string[]; genres: string[]; tracks: string[] }> {
  const token = await getSpotifyAppToken();
  const rawArtists = artistQuery
    .split(/[,;\n+]/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);

  if (rawArtists.length === 0) {
    throw new Error("Please specify at least one artist name or musical genre.");
  }

  const collectedGenres = new Set<string>();
  const verifiedArtists: string[] = [];
  const sampleTracks: string[] = [];

  if (token) {
    for (const artistName of rawArtists.slice(0, 8)) {
      try {
        const searchRes = await axios.get("https://api.spotify.com/v1/search", {
          params: {
            q: artistName,
            type: "artist,track",
            limit: 1,
          },
          headers: { Authorization: `Bearer ${token}` },
          timeout: 4000,
        });

        const artistObj = searchRes.data?.artists?.items?.[0];
        if (artistObj) {
          verifiedArtists.push(artistObj.name);
          if (Array.isArray(artistObj.genres)) {
            artistObj.genres.forEach((g: string) => collectedGenres.add(g.toLowerCase()));
          }
        } else {
          verifiedArtists.push(artistName);
        }

        const trackObj = searchRes.data?.tracks?.items?.[0];
        if (trackObj) {
          sampleTracks.push(`${trackObj.name} (${trackObj.artists?.[0]?.name || artistName})`);
        }
      } catch (err) {
        verifiedArtists.push(artistName);
      }
    }
  } else {
    // If Spotify keys are not provided, extrapolate realistic genres based on input
    verifiedArtists.push(...rawArtists);
    rawArtists.forEach((a) => {
      const lower = a.toLowerCase();
      if (lower.includes("rock") || lower.includes("metal") || lower.includes("pink floyd") || lower.includes("led zeppelin") || lower.includes("radiohead")) {
        collectedGenres.add("art rock");
        collectedGenres.add("alternative rock");
        collectedGenres.add("psychedelic rock");
      } else if (lower.includes("pop") || lower.includes("taylor") || lower.includes("dua") || lower.includes("ariana") || lower.includes("billie")) {
        collectedGenres.add("electropop");
        collectedGenres.add("dance pop");
        collectedGenres.add("indie pop");
      } else if (lower.includes("rap") || lower.includes("hip hop") || lower.includes("drake") || lower.includes("kendrick") || lower.includes("kanye")) {
        collectedGenres.add("conscious hip hop");
        collectedGenres.add("neo-soul");
        collectedGenres.add("jazz rap");
      } else if (lower.includes("jazz") || lower.includes("miles") || lower.includes("coltrane") || lower.includes("evans")) {
        collectedGenres.add("cool jazz");
        collectedGenres.add("modal jazz");
        collectedGenres.add("instrumental");
      } else if (lower.includes("ambient") || lower.includes("eno") || lower.includes("tycho") || lower.includes("bonobo")) {
        collectedGenres.add("ambient electronic");
        collectedGenres.add("downtempo");
        collectedGenres.add("chillwave");
      } else if (lower.includes("classical") || lower.includes("bach") || lower.includes("beethoven") || lower.includes("chopin") || lower.includes("zimmer")) {
        collectedGenres.add("neoclassical");
        collectedGenres.add("cinematic soundtrack");
        collectedGenres.add("piano");
      } else {
        collectedGenres.add(`${lower} style`);
        collectedGenres.add("indie");
        collectedGenres.add("alternative");
      }
    });
  }

  return {
    artists: verifiedArtists,
    genres: Array.from(collectedGenres).slice(0, 12),
    tracks: sampleTracks.slice(0, 5),
  };
}

// Generate psychological OCEAN report using Gemini API (@google/genai)
async function generateGeminiPsychologyReport(data: {
  identifier: string;
  genres: string[];
  artists?: string[];
  tracks?: string[];
}): Promise<{ report: string; scores: Finding["ocean_scores"]; archetype: string }> {
  const genresStr = data.genres.join(", ") || "diverse music genres";
  const artistsStr = (data.artists || []).join(", ") || data.identifier;
  const tracksStr = (data.tracks || []).join(", ") || "various favorite tracks";

  const systemInstruction = `You are a world-class Music Psychologist and Cognitive Neuroscientist specializing in musical preferences and the Big Five (OCEAN) personality framework.
Analyze the user's personality based on their Spotify listening DNA, artist preferences, and genre ecosystem.

Format your response strictly using this Markdown structure:

### 🧠 Psychological Profile: Big Five (OCEAN) Framework

#### **Dominant Traits**
* **Openness to Experience ([SCORE]% - [QUALIFIER])**: [Detailed psychological reasoning based on their musical choices]
* **Conscientiousness ([SCORE]% - [QUALIFIER])**: [Detailed psychological reasoning]
* **Extraversion ([SCORE]% - [QUALIFIER])**: [Detailed psychological reasoning]
* **Agreeableness ([SCORE]% - [QUALIFIER])**: [Detailed psychological reasoning]
* **Neuroticism / Emotional Receptivity ([SCORE]% - [QUALIFIER])**: [Detailed psychological reasoning]

---

#### **Musical Archetype: [ARCHETYPE NAME]**
[A 2-3 sentence evocative summary of their archetype]

---

#### **Emotional Regulation & Cognitive Style**
* **[STYLE NAME]**: [Insight into how they use Spotify and music for mood modulation, focus, or catharsis]

---

#### **Suggested Activity & Musical Prescription**
* **[ACTIVITY TITLE]**: [A tailored mindful activity and listening recommendation]

JSON_SCORES: {"openness": number, "conscientiousness": number, "extraversion": number, "agreeableness": number, "neuroticism": number, "archetype": "string"}`;

  const prompt = `Analyze this Spotify listener profile:
Artists: ${artistsStr}
Top Genres: ${genresStr}
Key Tracks/Context: ${tracksStr}
Identifier: @${data.identifier}`;

  if (process.env.GEMINI_API_KEY) {
    const candidateModels = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.7-flash"];
    for (const modelName of candidateModels) {
      try {
        const ai = getGemini();
        const response = await ai.models.generateContent({
          model: modelName,
          contents: `${systemInstruction}\n\n${prompt}`,
        });

        const rawText = response.text || "";
        if (rawText) {
          // Extract JSON_SCORES if present
          let parsedScores = { openness: 75, conscientiousness: 65, extraversion: 60, agreeableness: 70, neuroticism: 45 };
          let parsedArchetype = "The Sonic Explorer";

          const jsonMatch = rawText.match(/JSON_SCORES:\s*(\{[\s\S]*?\})/);
          let cleanedReport = rawText;
          if (jsonMatch) {
            try {
              const parsed = JSON.parse(jsonMatch[1]);
              parsedScores = {
                openness: Number(parsed.openness) || 75,
                conscientiousness: Number(parsed.conscientiousness) || 65,
                extraversion: Number(parsed.extraversion) || 60,
                agreeableness: Number(parsed.agreeableness) || 70,
                neuroticism: Number(parsed.neuroticism) || 45,
              };
              if (parsed.archetype) parsedArchetype = parsed.archetype;
              cleanedReport = rawText.replace(/JSON_SCORES:\s*\{[\s\S]*?\}/, "").trim();
            } catch {
              // Keep defaults
            }
          }

          // Check if archetype header exists
          const archetypeMatch = cleanedReport.match(/#### \*\*Musical Archetype:\s*([^\*]+)\*\*/i);
          if (archetypeMatch && archetypeMatch[1]) {
            parsedArchetype = archetypeMatch[1].trim();
          }

          return {
            report: cleanedReport,
            scores: parsedScores,
            archetype: parsedArchetype,
          };
        }
      } catch (err: unknown) {
        const errMsg = err instanceof Error ? err.message : String(err);
        console.warn(`Model ${modelName} call failed (${errMsg}), trying next available model...`);
      }
    }
  }

  // High-fidelity algorithmic psychological calculation if Gemini API key is missing
  const genreLower = genresStr.toLowerCase();
  const isOpen = genreLower.includes("ambient") || genreLower.includes("post-rock") || genreLower.includes("art") || genreLower.includes("experimental") || genreLower.includes("psychedelic") || genreLower.includes("classical") || genreLower.includes("jazz");
  const isExtraverted = genreLower.includes("dance") || genreLower.includes("pop") || genreLower.includes("hip hop") || genreLower.includes("house") || genreLower.includes("funk") || genreLower.includes("disco");
  const isConscientious = genreLower.includes("classical") || genreLower.includes("techno") || genreLower.includes("progressive") || genreLower.includes("soundtrack");
  const isAgreeable = genreLower.includes("indie") || genreLower.includes("folk") || genreLower.includes("soul") || genreLower.includes("r&b") || genreLower.includes("dream pop");
  const isIntrospective = genreLower.includes("shoegaze") || genreLower.includes("ambient") || genreLower.includes("lo-fi") || genreLower.includes("indie rock");

  const scores = {
    openness: isOpen ? 92 : 70,
    conscientiousness: isConscientious ? 80 : 60,
    extraversion: isExtraverted ? 85 : 42,
    agreeableness: isAgreeable ? 82 : 65,
    neuroticism: isIntrospective ? 56 : 38,
  };

  const archetype = isOpen && isIntrospective
    ? "The Atmospheric Architect"
    : isExtraverted
    ? "The Rhythmic Catalyst"
    : isOpen
    ? "The Avant-Garde Thinker"
    : "The Melodic Synthesizer";

  const fallbackReport = `### 🧠 Psychological Profile: Big Five (OCEAN) Framework

#### **Dominant Traits**
* **Openness to Experience (${scores.openness}% - ${scores.openness > 80 ? "Exceptionally High" : "High"})**: Distinct preference for layered textures and aesthetic nuance across **${genresStr}**. Demonstrates strong intellectual curiosity, active cognitive flexibility, and sensitivity to harmonic complexity.
* **Conscientiousness (${scores.conscientiousness}% - ${scores.conscientiousness > 70 ? "High" : "Moderate"})**: Shows purposeful curation and rhythmic consistency. Valuing structured composition, meticulous production, and steady listening flow.
* **Extraversion (${scores.extraversion}% - ${scores.extraversion > 65 ? "High / Outwardly Energized" : "Introspective / Reflective"})**: ${
    isExtraverted
      ? "Music acts as a social accelerant and motivational catalyst, reflecting enthusiasm, warmth, and dynamic energy."
      : "Preference for introspective, headphone-centric immersion over loud auditory environments. Uses music as an internal cognitive space."
  }
* **Agreeableness (${scores.agreeableness}% - ${scores.agreeableness > 75 ? "High Empathy" : "Balanced"})**: Strong emotional resonance with poignant vocal storytelling, empathetic themes, and organic instrumentals.
* **Neuroticism / Emotional Receptivity (${scores.neuroticism}% - ${scores.neuroticism > 50 ? "Empathetic Sensitivity" : "Calm Stability"})**: ${
    isIntrospective
      ? "Leverages deep atmospheric audio as a mindful container for processing emotions, winding down from cognitive fatigue, and sparking quiet ideas."
      : "Maintains high emotional baseline stability, utilizing music to reinforce positive and focused daily momentum."
  }

---

#### **Musical Archetype: ${archetype}**
You navigate music not merely as background sound, but as an intentional cognitive and emotional environment. Your listening profile balances distinct aesthetic discernment with emotional resonance.

---

#### **Emotional Regulation & Cognitive Style**
* **${isOpen || isIntrospective ? "Contemplative & Aesthetic Focusing" : "Rhythmic & Dopaminergic Modulation"}**: You utilize Spotify as a cognitive toolkit—synchronizing tempos with mental tasks to reduce friction, boost endurance, and induce flow states.

---

#### **Suggested Activity & Musical Prescription**
* **${
    isExtraverted
      ? "Collaborative Groove Session: Host a collaborative Spotify blend with close friends or fuel a high-intensity workout with an upbeat pulse playlist."
      : "Deep-Work Audio Immersion: Set a 50-minute focused sprint with high-fidelity noise-canceling headphones listening to full-album instrumental passages."
  }`;

  return { report: fallbackReport, scores, archetype };
}

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(cors());
  app.use(express.json());

  // Check Spotify and Gemini credentials status
  app.get("/api/status", (_req, res) => {
    res.json({
      hasGemini: !!process.env.GEMINI_API_KEY,
      hasSpotifyKeys: !!(process.env.SPOTIFY_CLIENT_ID && process.env.SPOTIFY_CLIENT_SECRET),
    });
  });

  // Spotify OAuth Authorization URL builder
  app.get("/api/auth/spotify/url", (req, res) => {
    const clientId = process.env.SPOTIFY_CLIENT_ID;
    if (!clientId) {
      res.status(400).json({
        error: "Spotify Client ID not configured. Please set SPOTIFY_CLIENT_ID in your environment.",
      });
      return;
    }

    const host = req.get("host") || "localhost:3000";
    const protocol = req.protocol === "https" || req.headers["x-forwarded-proto"] === "https" ? "https" : "http";
    const redirectUri = process.env.APP_URL
      ? `${process.env.APP_URL.replace(/\/$/, "")}/api/auth/spotify/callback`
      : `${protocol}://${host}/api/auth/spotify/callback`;

    const scopes = ["user-top-read", "user-read-recently-played", "user-read-private"];
    const params = new URLSearchParams({
      client_id: clientId,
      response_type: "code",
      redirect_uri: redirectUri,
      scope: scopes.join(" "),
      show_dialog: "true",
    });

    res.json({ url: `https://accounts.spotify.com/authorize?${params.toString()}` });
  });

  // Spotify OAuth Callback handler (Popup postMessage flow)
  app.get("/api/auth/spotify/callback", async (req, res) => {
    const code = req.query.code as string;
    const error = req.query.error as string;

    if (error || !code) {
      res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Spotify Auth Error</title></head>
        <body style="background:#0e1117;color:#fafafa;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;">
          <div style="text-align:center;">
            <h3>Spotify Authorization Failed</h3>
            <p style="color:#ef4444;">${error || "No authorization code provided."}</p>
            <script>
              window.opener && window.opener.postMessage({ type: 'SPOTIFY_AUTH_ERROR', error: '${error || "cancelled"}' }, '*');
              setTimeout(() => window.close(), 1500);
            </script>
          </div>
        </body>
        </html>
      `);
      return;
    }

    try {
      const clientId = process.env.SPOTIFY_CLIENT_ID;
      const clientSecret = process.env.SPOTIFY_CLIENT_SECRET;
      const host = req.get("host") || "localhost:3000";
      const protocol = req.protocol === "https" || req.headers["x-forwarded-proto"] === "https" ? "https" : "http";
      const redirectUri = process.env.APP_URL
        ? `${process.env.APP_URL.replace(/\/$/, "")}/api/auth/spotify/callback`
        : `${protocol}://${host}/api/auth/spotify/callback`;

      const authHeader = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");
      const tokenRes = await axios.post(
        "https://accounts.spotify.com/api/token",
        new URLSearchParams({
          grant_type: "authorization_code",
          code,
          redirect_uri: redirectUri,
        }).toString(),
        {
          headers: {
            Authorization: `Basic ${authHeader}`,
            "Content-Type": "application/x-www-form-urlencoded",
          },
          timeout: 8000,
        }
      );

      const accessToken = tokenRes.data?.access_token;

      // Fetch user profile and top artists
      let userName = "Spotify Listener";
      let topArtistsNames: string[] = [];
      let topGenres: string[] = [];
      let topTracksNames: string[] = [];

      if (accessToken) {
        try {
          const userProfileRes = await axios.get("https://api.spotify.com/v1/me", {
            headers: { Authorization: `Bearer ${accessToken}` },
            timeout: 5000,
          });
          userName = userProfileRes.data?.display_name || userProfileRes.data?.id || "Spotify User";

          const topArtistsRes = await axios.get("https://api.spotify.com/v1/me/top/artists?limit=10&time_range=medium_term", {
            headers: { Authorization: `Bearer ${accessToken}` },
            timeout: 5000,
          });

          const artists = topArtistsRes.data?.items || [];
          const genreSet = new Set<string>();
          artists.forEach((a: { name: string; genres: string[] }) => {
            topArtistsNames.push(a.name);
            (a.genres || []).forEach((g) => genreSet.add(g));
          });
          topGenres = Array.from(genreSet).slice(0, 10);

          const topTracksRes = await axios.get("https://api.spotify.com/v1/me/top/tracks?limit=5&time_range=medium_term", {
            headers: { Authorization: `Bearer ${accessToken}` },
            timeout: 5000,
          });
          topTracksNames = (topTracksRes.data?.items || []).map(
            (t: { name: string; artists: Array<{ name: string }> }) => `${t.name} - ${t.artists?.[0]?.name || ""}`
          );
        } catch (spotifyErr) {
          console.warn("Error fetching user top items:", spotifyErr);
        }
      }

      res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Spotify Connected</title></head>
        <body style="background:#0e1117;color:#fafafa;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;">
          <div style="text-align:center;">
            <h3 style="color:#1db954;">🎉 Spotify Connected Successfully!</h3>
            <p>Analyzing your musical personality with Gemini...</p>
            <script>
              const payload = {
                type: 'SPOTIFY_AUTH_SUCCESS',
                userName: ${JSON.stringify(userName)},
                topArtists: ${JSON.stringify(topArtistsNames)},
                topGenres: ${JSON.stringify(topGenres)},
                topTracks: ${JSON.stringify(topTracksNames)}
              };
              if (window.opener) {
                window.opener.postMessage(payload, '*');
              }
              setTimeout(() => window.close(), 1200);
            </script>
          </div>
        </body>
        </html>
      `);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      res.send(`
        <!DOCTYPE html>
        <html>
        <body style="background:#0e1117;color:#fafafa;font-family:sans-serif;padding:2rem;">
          <h3 style="color:#ef4444;">Spotify Token Exchange Error</h3>
          <p>${msg}</p>
          <script>
            window.opener && window.opener.postMessage({ type: 'SPOTIFY_AUTH_ERROR', error: '${msg}' }, '*');
            setTimeout(() => window.close(), 2000);
          </script>
        </body>
        </html>
      `);
    }
  });

  // Recent Findings
  app.get("/api/findings", (_req, res) => {
    res.json({ success: true, data: findingsStore.slice(0, 15) });
  });

  // Main Spotify Analysis Endpoint (supports Artists list, preset, or connected data)
  app.post("/api/analyze", async (req, res) => {
    const { source = "spotify_artists", query, artists, genres, tracks, identifier } = req.body;

    try {
      let finalIdentifier = (identifier || query || "Spotify Listener").trim();
      let finalGenres: string[] = Array.isArray(genres) ? genres : [];
      let finalArtists: string[] = Array.isArray(artists) ? artists : [];
      let finalTracks: string[] = Array.isArray(tracks) ? tracks : [];

      if (source === "spotify_artists" || source === "spotify_search") {
        const queryText = (query || identifier || "").trim();
        if (!queryText) {
          res.status(400).json({ success: false, error: "Please enter at least one artist, band, or genre." });
          return;
        }
        finalIdentifier = queryText;
        const details = await fetchSpotifyArtistDetails(queryText);
        finalArtists = details.artists;
        finalGenres = details.genres;
        finalTracks = details.tracks;
      }

      if (finalGenres.length === 0) {
        finalGenres = ["indie", "alternative", "modern pop", "soundtrack"];
      }

      const { report, scores, archetype } = await generateGeminiPsychologyReport({
        identifier: finalIdentifier,
        genres: finalGenres,
        artists: finalArtists,
        tracks: finalTracks,
      });

      const newFinding: Finding = {
        id: findingsStore.length + 1,
        source,
        identifier: finalIdentifier,
        genres_analyzed: finalGenres,
        top_artists: finalArtists.slice(0, 6),
        top_tracks: finalTracks.slice(0, 4),
        ocean_scores: scores,
        archetype,
        ocean_report: report,
        created_at: new Date().toISOString(),
      };

      findingsStore.unshift(newFinding);

      res.json({
        success: true,
        source,
        identifier: finalIdentifier,
        genres_analyzed: finalGenres,
        top_artists: finalArtists,
        top_tracks: finalTracks,
        ocean_scores: scores,
        archetype,
        ocean_report: report,
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      console.error("Spotify Analysis Error:", message);
      res.status(500).json({ success: false, error: message });
    }
  });

  // Vite Middleware in dev or static files in production
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*all", (_req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Personify (Spotify + Gemini) server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
