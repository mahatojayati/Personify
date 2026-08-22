import React, { useState, useEffect } from 'react';
import Markdown from 'react-markdown';
import {
  Sparkles,
  History,
  Music,
  User,
  Clock,
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Copy,
  Check,
  Disc3,
  ExternalLink,
  Layers,
  Radio,
  Sliders,
  Compass,
  Headphones,
  Zap,
} from 'lucide-react';
import { MusicalFinding, SpotifyAuthStatus } from './types';

const SPOTIFY_PRESETS = [
  {
    title: "Atmospheric & Dream Pop",
    artists: "Radiohead, Beach House, Tame Impala, Tycho",
    description: "Layered sonic textures, shoegaze harmonies, and introspective ambient grooves.",
    badge: "Introspective",
  },
  {
    title: "Upbeat Synth & Nu-Disco",
    artists: "Dua Lipa, Daft Punk, The Weeknd, Calvin Harris",
    description: "High-energy four-on-the-floor rhythms, driving basslines, and danceable hooks.",
    badge: "Energizing",
  },
  {
    title: "Conscious Hip-Hop & Neo-Soul",
    artists: "Kendrick Lamar, SZA, Frank Ocean, Tyler the Creator",
    description: "Lyrical depth, jazz-infused chords, dynamic flows, and soul storytelling.",
    badge: "Reflective",
  },
  {
    title: "Modern Classical & Cinematic",
    artists: "Max Richter, Ludovico Einaudi, Olafur Arnalds, Hans Zimmer",
    description: "Expansive piano arrangements, orchestral strings, and deep focus soundscapes.",
    badge: "Deep Focus",
  },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<'analyzer' | 'history'>('analyzer');
  const [inputArtists, setInputArtists] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentFinding, setCurrentFinding] = useState<MusicalFinding | null>(null);
  const [historyData, setHistoryData] = useState<MusicalFinding[]>([]);
  const [selectedHistoryFinding, setSelectedHistoryFinding] = useState<MusicalFinding | null>(null);
  const [copied, setCopied] = useState(false);
  const [authStatus, setAuthStatus] = useState<SpotifyAuthStatus>({
    authenticated: false,
    hasCredentials: false,
  });

  useEffect(() => {
    fetchHistory();
    checkApiStatus();

    // Listen for Spotify OAuth postMessage events from popup
    const handleAuthMessage = (event: MessageEvent) => {
      if (event.data?.type === 'SPOTIFY_AUTH_SUCCESS') {
        const { userName, topArtists, topGenres, topTracks } = event.data;
        analyzeSpotifyConnectedData(userName, topArtists, topGenres, topTracks);
      } else if (event.data?.type === 'SPOTIFY_AUTH_ERROR') {
        setError(`Spotify connection error: ${event.data.error || 'Authentication cancelled'}`);
        setLoading(false);
      }
    };

    window.addEventListener('message', handleAuthMessage);
    return () => window.removeEventListener('message', handleAuthMessage);
  }, []);

  const checkApiStatus = async () => {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      setAuthStatus((prev) => ({
        ...prev,
        hasCredentials: !!data.hasSpotifyKeys,
      }));
    } catch {
      // Ignore error
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/findings');
      const data = await res.json();
      if (data.success && Array.isArray(data.data)) {
        setHistoryData(data.data);
      }
    } catch (err) {
      console.warn('Failed to load history:', err);
    }
  };

  const handleAnalyzeArtists = async (artistsQuery?: string) => {
    const query = (artistsQuery || inputArtists).trim();
    if (!query) {
      setError('Please enter at least one artist, band, or musical genre.');
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentFinding(null);

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: 'spotify_artists',
          query,
        }),
      });

      const data = await res.json();
      if (data.success) {
        setCurrentFinding(data);
        fetchHistory();
      } else {
        setError(data.error || 'Failed to generate musical personality report.');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Network error during analysis.');
    } finally {
      setLoading(false);
    }
  };

  const analyzeSpotifyConnectedData = async (
    userName: string,
    topArtists: string[],
    topGenres: string[],
    topTracks: string[]
  ) => {
    setLoading(true);
    setError(null);
    setCurrentFinding(null);

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: 'spotify_connect',
          identifier: userName,
          artists: topArtists,
          genres: topGenres,
          tracks: topTracks,
        }),
      });

      const data = await res.json();
      if (data.success) {
        setCurrentFinding(data);
        fetchHistory();
      } else {
        setError(data.error || 'Failed to analyze connected Spotify data.');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Network error during connected analysis.');
    } finally {
      setLoading(false);
    }
  };

  const handleConnectSpotify = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/auth/spotify/url');
      const data = await res.json();

      if (data.url) {
        // Open Spotify authorization popup
        const width = 500;
        const height = 650;
        const left = window.screenX + (window.outerWidth - width) / 2;
        const top = window.screenY + (window.outerHeight - height) / 2;
        window.open(
          data.url,
          'SpotifyAuth',
          `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes,status=yes`
        );
      } else {
        setError('Spotify Client ID is not configured on the server. You can still analyze any Spotify artists or curated presets below!');
        setLoading(false);
      }
    } catch (err: unknown) {
      setError('Unable to initiate Spotify connection. Try searching by artist names below.');
      setLoading(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#f0f6fc] flex flex-col items-center px-4 py-8 sm:px-6 lg:px-8">
      <div className="w-full max-w-4xl space-y-6">
        {/* Header */}
        <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-800">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <Disc3 className="w-5 h-5 animate-spin-slow" />
              </div>
              <h1 id="app-title" className="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-center gap-2">
                Personify <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-normal border border-emerald-500/30">Spotify + Gemini</span>
              </h1>
            </div>
            <p className="text-gray-400 text-sm">
              Musical Psychology Mirror: Uncovering Big Five (OCEAN) personality traits from your Spotify audio DNA.
            </p>
          </div>

          {/* Quick Connect Spotify Button */}
          <button
            id="connect-spotify-btn"
            onClick={handleConnectSpotify}
            disabled={loading}
            className="self-start sm:self-auto flex items-center gap-2 px-4 py-2 bg-[#1DB954] hover:bg-[#1ed760] active:bg-[#1aa34a] text-black font-semibold text-xs rounded-full transition-colors shadow-sm cursor-pointer disabled:opacity-50"
          >
            <Radio className="w-3.5 h-3.5" />
            Connect Spotify Account
          </button>
        </header>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-gray-800/80">
          <button
            id="tab-analyzer-btn"
            onClick={() => setActiveTab('analyzer')}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 -mb-[2px] transition-colors cursor-pointer ${
              activeTab === 'analyzer'
                ? 'border-emerald-500 text-emerald-400 font-semibold'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Compass className="w-4 h-4" />
            Personality Analyzer
          </button>
          <button
            id="tab-history-btn"
            onClick={() => {
              setActiveTab('history');
              fetchHistory();
            }}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 -mb-[2px] transition-colors cursor-pointer ${
              activeTab === 'history'
                ? 'border-emerald-500 text-emerald-400 font-semibold'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <History className="w-4 h-4" />
            Community History ({historyData.length})
          </button>
        </div>

        {/* TAB 1: ANALYZER */}
        {activeTab === 'analyzer' && (
          <div className="space-y-6">
            {/* Input Card */}
            <div className="bg-[#161b22] border border-gray-800 rounded-xl p-5 sm:p-6 space-y-4">
              <div>
                <h2 className="text-base font-semibold text-white flex items-center gap-2">
                  <Headphones className="w-4 h-4 text-emerald-400" />
                  Analyze Your Spotify Listening Profile
                </h2>
                <p className="text-xs sm:text-sm text-gray-400 mt-1">
                  Enter your top Spotify artists, bands, or genre keywords separated by commas (e.g. <em>Radiohead, Tame Impala, Beach House</em>).
                </p>
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleAnalyzeArtists();
                }}
                className="space-y-3"
              >
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                    <Music className="w-4 h-4" />
                  </div>
                  <input
                    id="spotify-artists-input"
                    type="text"
                    value={inputArtists}
                    onChange={(e) => setInputArtists(e.target.value)}
                    placeholder="e.g. Tame Impala, Phoebe Bridgers, Frank Ocean, Daft Punk"
                    className="w-full pl-10 pr-4 py-2.5 bg-[#0d1117] border border-gray-700 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
                  />
                </div>

                <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <Zap className="w-3.5 h-3.5 text-amber-400" />
                    <span>Gemini 3.7 Flash cognitive psychological modeling</span>
                  </div>

                  <button
                    id="submit-analysis-btn"
                    type="submit"
                    disabled={loading}
                    className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 disabled:opacity-50 text-white text-xs sm:text-sm font-medium rounded-lg transition-all flex items-center gap-2 cursor-pointer shadow-sm ml-auto"
                  >
                    {loading ? (
                      <>
                        <Disc3 className="w-4 h-4 animate-spin" />
                        <span>Analyzing with Gemini...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        <span>Generate Psychology Mirror</span>
                      </>
                    )}
                  </button>
                </div>
              </form>

              {/* Curated Presets */}
              <div className="pt-4 border-t border-gray-800/80">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-emerald-400" />
                  Or Try a Curated Spotify Archetype
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {SPOTIFY_PRESETS.map((preset, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setInputArtists(preset.artists);
                        handleAnalyzeArtists(preset.artists);
                      }}
                      disabled={loading}
                      className="p-3 text-left bg-[#0d1117] hover:bg-[#1f242c] border border-gray-800 hover:border-gray-700 rounded-lg transition-all cursor-pointer group"
                    >
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="text-xs font-semibold text-white group-hover:text-emerald-400 transition-colors">
                          {preset.title}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 font-medium">
                          {preset.badge}
                        </span>
                      </div>
                      <p className="text-[11px] text-gray-400 truncate">{preset.artists}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Error Alert */}
            {error && (
              <div id="error-alert" className="p-4 bg-red-950/40 border border-red-800/80 rounded-xl flex items-start gap-3 text-red-200 text-sm">
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold text-red-300">Analysis Notice</p>
                  <p className="text-xs mt-0.5 text-red-200/90">{error}</p>
                </div>
              </div>
            )}

            {/* Loading Indicator */}
            {loading && (
              <div className="p-8 bg-[#161b22] border border-gray-800 rounded-xl flex flex-col items-center justify-center text-center space-y-3">
                <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 animate-pulse">
                  <Sparkles className="w-6 h-6" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-sm font-semibold text-white">Gemini Cognitive Engine is Processing</h3>
                  <p className="text-xs text-gray-400 max-w-sm">
                    Extracting Spotify sonic markers, calculating OCEAN trait percentiles, and synthesising psychological insights...
                  </p>
                </div>
              </div>
            )}

            {/* Active Finding Report */}
            {currentFinding && !loading && (
              <div id="report-section" className="space-y-5">
                {/* Result Top Card: Archetype & OCEAN Trait Bars */}
                <div className="bg-[#161b22] border border-emerald-500/30 rounded-xl p-5 sm:p-6 space-y-5">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-800 pb-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                        <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                          Psychological Profile Ready
                        </span>
                      </div>
                      <h2 className="text-xl font-bold text-white mt-1 flex items-center gap-2">
                        {currentFinding.archetype || 'The Sonic Explorer'}
                      </h2>
                      <p className="text-xs text-gray-400 mt-0.5">
                        Profiled for: <span className="text-gray-200 font-medium">{currentFinding.identifier}</span>
                      </p>
                    </div>

                    <button
                      onClick={() => handleCopy(currentFinding.ocean_report)}
                      className="inline-flex items-center gap-1.5 text-xs text-gray-300 hover:text-white bg-[#0d1117] hover:bg-gray-800 border border-gray-700 px-3 py-1.5 rounded-lg transition-colors self-start sm:self-auto cursor-pointer"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      {copied ? 'Copied' : 'Copy Report'}
                    </button>
                  </div>

                  {/* Big Five Metric Meters */}
                  {currentFinding.ocean_scores && (
                    <div className="space-y-3">
                      <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400 flex items-center gap-1.5">
                        <Sliders className="w-3.5 h-3.5 text-emerald-400" />
                        Big Five (OCEAN) Trait Distribution
                      </h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 text-xs">
                        {/* Openness */}
                        <div className="space-y-1 bg-[#0d1117] p-2.5 rounded-lg border border-gray-800">
                          <div className="flex justify-between font-medium">
                            <span className="text-gray-300">Openness to Experience</span>
                            <span className="text-emerald-400 font-bold">{currentFinding.ocean_scores.openness}%</span>
                          </div>
                          <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${currentFinding.ocean_scores.openness}%` }}
                            />
                          </div>
                        </div>

                        {/* Conscientiousness */}
                        <div className="space-y-1 bg-[#0d1117] p-2.5 rounded-lg border border-gray-800">
                          <div className="flex justify-between font-medium">
                            <span className="text-gray-300">Conscientiousness</span>
                            <span className="text-blue-400 font-bold">{currentFinding.ocean_scores.conscientiousness}%</span>
                          </div>
                          <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${currentFinding.ocean_scores.conscientiousness}%` }}
                            />
                          </div>
                        </div>

                        {/* Extraversion */}
                        <div className="space-y-1 bg-[#0d1117] p-2.5 rounded-lg border border-gray-800">
                          <div className="flex justify-between font-medium">
                            <span className="text-gray-300">Extraversion</span>
                            <span className="text-amber-400 font-bold">{currentFinding.ocean_scores.extraversion}%</span>
                          </div>
                          <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-amber-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${currentFinding.ocean_scores.extraversion}%` }}
                            />
                          </div>
                        </div>

                        {/* Agreeableness */}
                        <div className="space-y-1 bg-[#0d1117] p-2.5 rounded-lg border border-gray-800">
                          <div className="flex justify-between font-medium">
                            <span className="text-gray-300">Agreeableness</span>
                            <span className="text-purple-400 font-bold">{currentFinding.ocean_scores.agreeableness}%</span>
                          </div>
                          <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${currentFinding.ocean_scores.agreeableness}%` }}
                            />
                          </div>
                        </div>

                        {/* Neuroticism */}
                        <div className="space-y-1 bg-[#0d1117] p-2.5 rounded-lg border border-gray-800 sm:col-span-2">
                          <div className="flex justify-between font-medium">
                            <span className="text-gray-300">Emotional Sensitivity / Receptivity</span>
                            <span className="text-rose-400 font-bold">{currentFinding.ocean_scores.neuroticism}%</span>
                          </div>
                          <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-rose-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${currentFinding.ocean_scores.neuroticism}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Genres and Artists analyzed */}
                  <div className="pt-2 flex flex-wrap gap-2">
                    {currentFinding.genres_analyzed?.map((genre, idx) => (
                      <span
                        key={idx}
                        className="text-xs bg-[#0d1117] text-gray-300 px-2.5 py-1 rounded-md border border-gray-700/60 flex items-center gap-1.5"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                        {genre}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Markdown Psychological Narrative */}
                <div className="bg-[#161b22] border border-gray-800 rounded-xl p-5 sm:p-7 text-gray-200">
                  <div className="prose prose-invert max-w-none prose-headings:text-gray-100 prose-h3:text-lg prose-h4:text-base prose-p:text-gray-300 prose-p:leading-relaxed prose-li:text-gray-300 prose-strong:text-white prose-hr:border-gray-800">
                    <Markdown>{currentFinding.ocean_report}</Markdown>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: HISTORY */}
        {activeTab === 'history' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-white">Recent Personality Analyses</h2>
                <p className="text-xs text-gray-400">Historical Big Five profiles analyzed by Gemini.</p>
              </div>
              <button
                onClick={fetchHistory}
                className="text-xs text-gray-300 hover:text-white bg-[#161b22] hover:bg-gray-800 border border-gray-700 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
              >
                Refresh List
              </button>
            </div>

            {historyData.length > 0 ? (
              <div className="space-y-4">
                <div className="overflow-x-auto rounded-xl border border-gray-800 bg-[#161b22]">
                  <table className="w-full text-left text-sm text-gray-300">
                    <thead className="bg-[#0d1117] text-xs uppercase font-semibold text-gray-400 border-b border-gray-800">
                      <tr>
                        <th className="px-4 py-3">Profile / Artists</th>
                        <th className="px-4 py-3">Archetype</th>
                        <th className="px-4 py-3">Analyzed Genres</th>
                        <th className="px-4 py-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800/60">
                      {historyData.map((item, idx) => (
                        <tr key={item.id || idx} className="hover:bg-[#1c2128] transition-colors">
                          <td className="px-4 py-3.5 font-medium text-white whitespace-nowrap">
                            <div className="flex items-center gap-2">
                              <span className="w-2 h-2 rounded-full bg-emerald-400 shrink-0"></span>
                              <span className="truncate max-w-[180px]">{item.identifier}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3.5 text-xs text-emerald-400 font-medium whitespace-nowrap">
                            {item.archetype || 'The Sonic Explorer'}
                          </td>
                          <td className="px-4 py-3.5 text-xs text-gray-400 max-w-xs truncate">
                            {item.genres_analyzed?.join(', ')}
                          </td>
                          <td className="px-4 py-3.5 text-right whitespace-nowrap">
                            <button
                              onClick={() => setSelectedHistoryFinding(item)}
                              className="inline-flex items-center gap-1 text-xs text-emerald-400 hover:text-emerald-300 font-medium cursor-pointer"
                            >
                              View Report <ChevronRight className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Selected History Modal / Expander */}
                {selectedHistoryFinding && (
                  <div className="p-5 sm:p-6 bg-[#161b22] border border-gray-800 rounded-xl space-y-4">
                    <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-white">
                            {selectedHistoryFinding.archetype || 'Psychological Finding'}
                          </h3>
                          <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                            {selectedHistoryFinding.identifier}
                          </span>
                        </div>
                        <p className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                          <Clock className="w-3 h-3" />
                          {selectedHistoryFinding.created_at
                            ? new Date(selectedHistoryFinding.created_at).toLocaleString()
                            : 'Historical record'}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleCopy(selectedHistoryFinding.ocean_report)}
                          className="text-xs bg-[#0d1117] hover:bg-gray-800 text-gray-300 px-3 py-1.5 rounded-lg border border-gray-700 transition-colors cursor-pointer"
                        >
                          Copy
                        </button>
                        <button
                          onClick={() => setSelectedHistoryFinding(null)}
                          className="text-xs text-gray-400 hover:text-white px-2 py-1.5 cursor-pointer"
                        >
                          ✕ Close
                        </button>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1.5">
                      {selectedHistoryFinding.genres_analyzed?.map((g, i) => (
                        <span key={i} className="text-xs bg-[#0d1117] text-gray-300 px-2 py-0.5 rounded border border-gray-800">
                          {g}
                        </span>
                      ))}
                    </div>

                    <div className="pt-2 border-t border-gray-800/80">
                      <div className="prose prose-invert max-w-none text-sm prose-headings:text-gray-100 prose-p:text-gray-300 prose-li:text-gray-300">
                        <Markdown>{selectedHistoryFinding.ocean_report}</Markdown>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 bg-[#161b22] border border-gray-800 rounded-xl text-center text-gray-400 text-sm">
                No previous analyses found. Generate your first profile in the Analyzer tab!
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <footer className="pt-6 border-t border-gray-800/80 text-center space-y-1">
          <p className="text-xs text-gray-500">
            Personify • Powered by Spotify Web API & Google Gemini 3.7 Flash • Big Five (OCEAN) Framework
          </p>
        </footer>
      </div>
    </div>
  );
}
