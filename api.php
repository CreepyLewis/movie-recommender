<?php
/**
 * api.php — Creepy Movie Recommendation
 * PHP backend: receives requests from JS, calls TMDB API, returns JSON.
 *
 * SETUP: Replace YOUR_TMDB_API_KEY_HERE with your actual TMDB key.
 */

// ── Config ────────────────────────────────────────────────────────
define('TMDB_KEY',  'YOUR_TMDB_API_KEY_HERE');   // ← paste your key here
define('BASE_URL',  'https://api.themoviedb.org/3');
define('IMG_BASE',  'https://image.tmdb.org/t/p/w500');
define('LOGO_BASE', 'https://image.tmdb.org/t/p/w200');

// ── CORS + JSON headers ───────────────────────────────────────────
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// ── Input sanitisation ────────────────────────────────────────────
$action = isset($_GET['action']) ? htmlspecialchars(strip_tags(trim($_GET['action']))) : 'popular';
$query  = isset($_GET['query'])  ? htmlspecialchars(strip_tags(trim($_GET['query'])))  : '';
$id     = isset($_GET['id'])     ? (int)$_GET['id']                                   : 0;
$genre  = isset($_GET['genre'])  ? htmlspecialchars(strip_tags(trim($_GET['genre'])))  : '';

// ── Helper: call TMDB and return decoded JSON ─────────────────────
function tmdb(string $endpoint, array $extra = []): array {
    $params = array_merge(['api_key' => TMDB_KEY], $extra);
    $url    = BASE_URL . $endpoint . '?' . http_build_query($params);

    $ctx  = stream_context_create(['http' => ['timeout' => 8]]);
    $raw  = @file_get_contents($url, false, $ctx);

    if ($raw === false) {
        return ['error' => 'TMDB request failed'];
    }
    return json_decode($raw, true) ?? ['error' => 'Invalid JSON from TMDB'];
}

// ── Helper: shape a movie for the frontend ────────────────────────
function shape_movie(array $m): array {
    return [
        'id'          => $m['id']           ?? null,
        'title'       => $m['title']        ?? 'Unknown',
        'overview'    => $m['overview']     ?? '',
        'rating'      => $m['vote_average'] ?? 0,
        'release'     => $m['release_date'] ?? '',
        'poster'      => !empty($m['poster_path'])   ? IMG_BASE  . $m['poster_path']   : null,
        'backdrop'    => !empty($m['backdrop_path']) ? 'https://image.tmdb.org/t/p/w1280' . $m['backdrop_path'] : null,
    ];
}

// ── Router ────────────────────────────────────────────────────────
switch ($action) {

    // ── Popular movies ────────────────────────────────────────────
    case 'popular':
        $data = tmdb('/movie/popular');
        echo json_encode([
            'status'  => 'ok',
            'section' => '🔥 Popular Now',
            'movies'  => array_map('shape_movie', $data['results'] ?? []),
        ]);
        break;

    // ── Genre browsing ────────────────────────────────────────────
    case 'genre':
        $genre_ids = [
            'horror'   => 27,
            'action'   => 28,
            'comedy'   => 35,
            'romance'  => 10749,
            'thriller' => 53,
            'scifi'    => 878,
        ];
        $labels = [
            'horror'   => '👻 Horror',
            'action'   => '💥 Action',
            'comedy'   => '😂 Comedy',
            'romance'  => '❤️ Romance',
            'thriller' => '🔪 Thriller',
            'scifi'    => '🚀 Sci-Fi',
        ];
        $gid = $genre_ids[$genre] ?? 27;
        $data = tmdb('/discover/movie', ['with_genres' => $gid, 'sort_by' => 'popularity.desc']);
        echo json_encode([
            'status'  => 'ok',
            'section' => $labels[$genre] ?? '🎬 Movies',
            'movies'  => array_map('shape_movie', $data['results'] ?? []),
        ]);
        break;

    // ── Search ────────────────────────────────────────────────────
    case 'search':
        if (empty($query)) {
            echo json_encode(['status' => 'error', 'message' => 'Search query is empty.']);
            break;
        }
        $data = tmdb('/search/movie', ['query' => $query]);
        $movies = array_map('shape_movie', $data['results'] ?? []);
        echo json_encode([
            'status'  => 'ok',
            'section' => "🔍 Results for \"" . htmlspecialchars($query) . "\"",
            'movies'  => $movies,
            'total'   => $data['total_results'] ?? 0,
        ]);
        break;

    // ── Movie details ─────────────────────────────────────────────
    case 'details':
        if ($id <= 0) {
            echo json_encode(['status' => 'error', 'message' => 'Invalid movie ID.']);
            break;
        }

        // Fetch details, credits, videos, watch providers in parallel (sequential here)
        $detail    = tmdb("/movie/{$id}");
        $credits   = tmdb("/movie/{$id}/credits");
        $videos    = tmdb("/movie/{$id}/videos");
        $providers = tmdb("/movie/{$id}/watch/providers");

        // Shape trailer
        $trailer = null;
        foreach (($videos['results'] ?? []) as $v) {
            if ($v['type'] === 'Trailer' && $v['site'] === 'YouTube') {
                $trailer = "https://www.youtube.com/embed/{$v['key']}?autoplay=0&rel=0";
                break;
            }
        }

        // Shape cast (top 6)
        $cast = [];
        foreach (array_slice($credits['cast'] ?? [], 0, 6) as $actor) {
            $cast[] = [
                'name'   => $actor['name']         ?? '',
                'char'   => $actor['character']    ?? '',
                'photo'  => !empty($actor['profile_path']) ? IMG_BASE . $actor['profile_path'] : null,
            ];
        }

        // Shape genres
        $genres = array_column($detail['genres'] ?? [], 'name');

        // Shape watch providers (Kenya)
        $ke = ($providers['results'] ?? [])['KE'] ?? [];
        $watch = [];
        foreach (['flatrate', 'rent', 'buy'] as $cat) {
            if (!empty($ke[$cat])) {
                $watch[$cat] = array_map(fn($p) => [
                    'name' => $p['provider_name'] ?? '',
                    'logo' => !empty($p['logo_path']) ? LOGO_BASE . $p['logo_path'] : null,
                ], $ke[$cat]);
            }
        }
        if (!empty($ke['link'])) $watch['link'] = $ke['link'];

        echo json_encode([
            'status'   => 'ok',
            'movie'    => array_merge(shape_movie($detail), [
                'runtime'    => $detail['runtime']     ?? null,
                'tagline'    => $detail['tagline']     ?? '',
                'genres'     => $genres,
                'budget'     => $detail['budget']      ?? 0,
                'revenue'    => $detail['revenue']     ?? 0,
                'imdb_id'    => $detail['imdb_id']     ?? '',
            ]),
            'trailer'  => $trailer,
            'cast'     => $cast,
            'watch'    => $watch,
        ]);
        break;

    // ── Now playing in cinemas ─────────────────────────────────────
    case 'nowplaying':
        $data = tmdb('/movie/now_playing', ['region' => 'KE']);
        echo json_encode([
            'status'  => 'ok',
            'section' => '🎟 Now Showing in Cinemas',
            'movies'  => array_map('shape_movie', $data['results'] ?? []),
        ]);
        break;

    // ── Unknown action ────────────────────────────────────────────
    default:
        http_response_code(400);
        echo json_encode(['status' => 'error', 'message' => "Unknown action: {$action}"]);
}
