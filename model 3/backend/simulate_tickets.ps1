$baseUrl = "http://127.0.0.1:8000/api/reports"

function Create-Report($desc, $lat, $lon) {
    $payload = @{
        description = $desc
        latitude = $lat
        longitude = $lon
        citizen_name = "Test Citizen"
        citizen_phone = "9999999999"
        address_text = "Simulated Location"
        source = "web"
    } | ConvertTo-Json
    
    echo "Sending: $desc"
    curl.exe -X POST $baseUrl -H "Content-Type: application/json" --data "$($payload.Replace('"', '\"'))"
    echo "`n-------------------"
}

# 1. Clustering Demo
$centerLat = 28.7041
$centerLon = 77.1025

Create-Report "Huge pothole near the park" ($centerLat + 0.001) ($centerLon + 0.001)
Create-Report "Dangerous dip in the road" ($centerLat + 0.0011) ($centerLon + 0.0011)
Create-Report "Road damage is causing accidents" ($centerLat + 0.0009) ($centerLon + 0.0009)

# 2. Urgency Demo
Create-Report "SPARKING TRANSFORMER! DANGEROUS!" ($centerLat - 0.001) ($centerLon - 0.001)

# 3. Spread
Create-Report "Water leakage from main pipe" ($centerLat + 0.002) ($centerLon - 0.002)
Create-Report "Garbage pileup behind the market" ($centerLat - 0.002) ($centerLon + 0.002)
Create-Report "Street light not working for 3 days" ($centerLat + 0.003) ($centerLon + 0.001)
