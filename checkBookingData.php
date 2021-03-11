<?php

$host = "localhost";
$dbname = "SFM";
$username = "esp32";
$password = "esp_boss5";



try{
	$conn = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
	echo "Connected to $dbname at $host successfully.";

	if ($_SERVER["REQUEST_METHOD"] == "POST"){

		$sensor = filter_var($_POST["sensor"],FILTER_SANITIZE_STRING);
		$location = filter_var($_POST["location"],FILTER_SANITIZE_STRING);
		$rfid = filter_var($_POST["rfid"],FILTER_SANITIZE_STRING);

        $range = bookingStart 

		$sql = "SELECT FROM Booking WHERE bookdate AND booktime between bookingStart and bookingEnd";
		

		$stmt = $conn->prepare($sql);

		$stmt->bindParam(":sensor", $sensor);
		$stmt->bindParam(":location", $location);
		$stmt->bindParam(":rfid", $rfid);

		$result = $stmt->execute();

		if($result == TRUE){
			echo "Data Posted Successfully";
		}
		else{
			echo "Data Post Unsuccessful";

		}
		$conn = null;
	}
}
catch (PDOException $pe){
	die("Could not connect to the database $dbname :" . $pe->getMessage());
}

?>
