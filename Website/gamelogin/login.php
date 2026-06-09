<?php
// Command
// curl -X POST https://tbox.mllhild.com/gamelogin/login.php -H "Content-Type: application/json" -d '{"login":"Hild","password":"Hild"}'

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *"); // allow requests from any domain (adjust if needed)
header("Access-Control-Allow-Methods: POST");

// Database connection settings
$dbHost = "localhost";
$dbUser = "---------------------------";
$dbPass = "---------------------------";
$dbName = "db_webapp";

// Connect to database
$conn = new mysqli($dbHost, $dbUser, $dbPass, $dbName);

// Check connection
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "Database connection failed"]). "\n";
    exit();
}

// Get POST data
$data = json_decode(file_get_contents("php://input"), true);
$username = trim($data['login'] ?? '');
$password = trim($data['password'] ?? '');

if (empty($username) || empty($password)) {
    http_response_code(400);
    echo json_encode(["error" => "Username and password are required"]). "\n";
    exit();
}

// Prepare SQL statement
$stmt = $conn->prepare("SELECT id, password FROM tb_user_dev WHERE login = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
$result = $stmt->get_result();

// Verify user
if ($row = $result->fetch_assoc()) {
    //if ($password === $row['password']){
    if (password_verify($password, $row['password'])) {
        // Generate a token (you could also use JWT)
        $token = bin2hex(random_bytes(32));

        // Store token in DB (optional for tracking sessions)
        $stmt2 = $conn->prepare("UPDATE tb_user_dev SET token = ?, token_expiry = DATE_ADD(NOW(), INTERVAL 1 HOUR) WHERE id = ?");
        $stmt2->bind_param("si", $token, $row['id']);
        $stmt2->execute();

        echo json_encode([
            "success" => true,
            "token" => $token
        ]). "\n";
        
    } else {
        http_response_code(401);
        echo json_encode(["error" => "Invalid credentials - p1"]). "\n";
    }
} else {
    http_response_code(401);
    echo json_encode(["error" => "Invalid credentials - p2"]). "\n";
}

$conn->close();
?>
