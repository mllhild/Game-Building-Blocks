<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST");

// --- Pure PHP JWT functions ---
function jwt_encode(array $payload, string $secret, string $alg = 'HS256'): string {
    $header = ['typ' => 'JWT', 'alg' => $alg];

    $base64UrlEncode = function($data) {
        return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
    };

    $headerEncoded = $base64UrlEncode(json_encode($header));
    $payloadEncoded = $base64UrlEncode(json_encode($payload));

    $signature = hash_hmac('sha256', "$headerEncoded.$payloadEncoded", $secret, true);
    $signatureEncoded = $base64UrlEncode($signature);

    return "$headerEncoded.$payloadEncoded.$signatureEncoded";
}

function jwt_decode(string $jwt, string $secret, string $alg = 'HS256') {
    $base64UrlDecode = function($data) {
        $remainder = strlen($data) % 4;
        if ($remainder) $data .= str_repeat('=', 4 - $remainder);
        return base64_decode(strtr($data, '-_', '+/'));
    };

    $parts = explode('.', $jwt);
    if (count($parts) !== 3) throw new Exception("Invalid JWT format");

    list($headerEncoded, $payloadEncoded, $signatureEncoded) = $parts;

    $header = json_decode($base64UrlDecode($headerEncoded), true);
    $payload = json_decode($base64UrlDecode($payloadEncoded), true);
    $signature = $base64UrlDecode($signatureEncoded);

    $expectedSig = hash_hmac('sha256', "$headerEncoded.$payloadEncoded", $secret, true);

    if (!hash_equals($expectedSig, $signature)) throw new Exception("Invalid signature");

    // Check expiration
    if (isset($payload['exp']) && time() > $payload['exp']) throw new Exception("Token expired");

    return $payload;
}

// --- Main login logic ---
try {
    // Database connection
    $dbHost = "localhost";
    $dbUser = ""---------------------------";";
    $dbPass = "---------------------------";
    $dbName = "db_webapp";

    $conn = new mysqli($dbHost, $dbUser, $dbPass, $dbName);
    if ($conn->connect_error) {
        throw new Exception("Database connection failed: " . $conn->connect_error);
    }

    // Get POST data
    $data = json_decode(file_get_contents("php://input"), true);
    $username = trim($data['login'] ?? '');
    $password = trim($data['password'] ?? '');

    if (empty($username) || empty($password)) {
        http_response_code(400);
        echo json_encode(["error" => "Username and password are required"]);
        exit();
    }

    // Fetch user
    $stmt = $conn->prepare("SELECT id, password FROM tb_user_dev WHERE login = ?");
    if (!$stmt) throw new Exception("Prepare statement failed: " . $conn->error);
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($row = $result->fetch_assoc()) {
        if (password_verify($password, $row['password'])) {
            // Generate JWT
            $secretKey = 'mySuperSecretKey123!'; // change to a strong secret
            $issuedAt = time();
            $expiration = $issuedAt + 3600; // 1 hour validity

            $payload = [
                'iat' => $issuedAt,
                'exp' => $expiration,
                'uid' => $row['id'],
                'username' => $username
            ];

            $jwt = jwt_encode($payload, $secretKey);

            echo json_encode([
                "success" => true,
                "token" => $jwt
            ]);
        } else {
            http_response_code(401);
            echo json_encode(["error" => "Invalid credentials"]);
        }
    } else {
        http_response_code(401);
        echo json_encode(["error" => "Invalid credentials"]);
    }

} catch (\Throwable $e) {
    http_response_code(500);
    echo json_encode(["error" => $e->getMessage()]);
}
