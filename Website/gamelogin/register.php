<?php
// Command
// curl -X POST https://tbox.mllhild.com/gamelogin/register.php -H "Content-Type: application/json" -d '{"login":"Peroth","password":"Peroth"}'

// Enable error reporting for debugging (remove in production)
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST");

// Database connection settings
$dbHost = "localhost";
$dbUser = "---------------------------";
$dbPass = "---------------------------";
$dbName = "db_webapp";

// Connect to database
$conn = new mysqli($dbHost, $dbUser, $dbPass, $dbName);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "Database connection failed"]). "\n";
    exit();
}

// Get POST data
$data = json_decode(file_get_contents("php://input"), true);
$login = trim($data['login'] ?? '');
$password = trim($data['password'] ?? '');

if (empty($login) || empty($password)) {
    http_response_code(400);
    echo json_encode(["error" => "login and password are required"]). "\n";
    exit();
}

// Check if login exists
$stmt = $conn->prepare("SELECT id FROM tb_user_dev WHERE login = ?");
$stmt->bind_param("s", $login);
$stmt->execute();
$stmt->store_result();
if ($stmt->num_rows > 0) {
    http_response_code(409); // conflict
    echo json_encode(["error" => "login already exists"]). "\n";
    $stmt->close();
    $conn->close();
    exit();
}
$stmt->close();

// Hash password
$hash = password_hash($password, PASSWORD_DEFAULT);

// Insert new user
$stmt = $conn->prepare("INSERT INTO tb_user_dev (login, password) VALUES (?, ?)");
$stmt->bind_param("ss", $login, $hash);

if ($stmt->execute()) {
    echo json_encode(["success" => true, "message" => "User registered successfully"]). "\n";
} else {
    http_response_code(500);
    echo json_encode(["error" => "Failed to register user"]). "\n";
}

$stmt->close();
$conn->close();
?>
