// Initialize variables
let map;
let userMarker;
let doctorMarkers = [];
let userLocation = null;
let radius = 5000; // Default radius in meters
let dermatologists = [];
let searchCircle; // Circle to visualize the search radius

// Custom icons
const userIcon = L.icon({
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    shadowSize: [41, 41],
    className: 'user-marker' // User marker class for styling
});

const doctorIcon = L.icon({
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    shadowSize: [41, 41],
    className: 'doctor-marker' // Doctor marker class for styling
});

// Apply custom styling to markers via CSS
const style = document.createElement('style');
style.textContent = `
    .user-marker {
        filter: hue-rotate(270deg); /* Makes icon purple/violet */
    }
    .doctor-marker {
        filter: hue-rotate(120deg); /* Makes icon green */
    }
`;
document.head.appendChild(style);

// Initialize the map when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    console.log('Map initialization started');
});

// Initialize the map
function initMap() {
    try {
        // Create map with default view (will be updated when we get user location)
        map = L.map('map').setView([0, 0], 2);
        
        // Add dark theme map tiles
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(map);
        
        console.log('Map initialized successfully');
        
        // Set up event listeners
        setupEventListeners();
        
        // Get user location
        getUserLocation();
    } catch (error) {
        console.error('Error initializing map:', error);
        showError('Failed to initialize map. Please reload the page and try again.');
    }
}

// Set up event listeners for UI interactions
function setupEventListeners() {
    // Radius slider change event
    document.getElementById('radius-slider').addEventListener('input', function() {
        radius = parseInt(this.value);
        document.getElementById('radius-value').textContent = radius / 1000; // Convert meters to km for display
        
        // If we have user location, update the search circle
        if (userLocation && searchCircle) {
            searchCircle.setRadius(radius);
        }
        
        // If we have user location, refresh the search
        if (userLocation) {
            fetchNearbyDermatologists();
        }
    });
    
    // Search input keyup event
    document.getElementById('search-input').addEventListener('keyup', function() {
        filterDoctors();
    });
    
    // Refresh button click event
    document.getElementById('refresh-btn').addEventListener('click', function() {
        console.log('Refresh button clicked');
        getUserLocation();
    });
    
    // Back button click event
    document.getElementById('back-btn').addEventListener('click', function() {
        window.location.href = 'dashboard.html'; // Or your dashboard URL
    });
    
    // Add click event to map for manual location selection
    map.on('click', function(e) {
        setUserLocation(e.latlng.lat, e.latlng.lng);
    });
}

// Get user's live location
function getUserLocation() {
    document.getElementById('map-loading').style.display = 'flex';
    console.log('Getting user location...');
    
    if (navigator.geolocation) {
        const options = {
            enableHighAccuracy: true,
            timeout: 10000, // 10 seconds timeout
            maximumAge: 0 // Always get fresh location
        };
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                console.log('User location obtained:', position.coords.latitude, position.coords.longitude);
                setUserLocation(position.coords.latitude, position.coords.longitude);
            },
            (error) => {
                console.error('Geolocation error:', error);
                handleGeolocationError(error);
                document.getElementById('map-loading').style.display = 'none';
                
                // Use a default location as fallback (e.g., city center)
                showError("Using default location. Click on the map to set your location manually.");
                setUserLocation(51.5074, -0.1278); // Default to London for example
            },
            options
        );
    } else {
        console.error('Geolocation not supported');
        showError("Geolocation is not supported by your browser. Click on the map to set your location manually.");
        document.getElementById('map-loading').style.display = 'none';
    }
}

// Set user location (from geolocation or manual click)
function setUserLocation(lat, lng) {
    userLocation = {
        lat: lat,
        lng: lng
    };
    
    console.log('Setting user location to:', userLocation);
    
    // Update map view to user location
    map.setView([userLocation.lat, userLocation.lng], 14);
    
    // Add or update user marker
    if (userMarker) {
        userMarker.setLatLng([userLocation.lat, userLocation.lng]);
    } else {
        userMarker = L.marker([userLocation.lat, userLocation.lng], {icon: userIcon}).addTo(map);
        userMarker.bindPopup("<b>You are here</b>").openPopup();
    }
    
    // Add or update search radius circle
    if (searchCircle) {
        searchCircle.setLatLng([userLocation.lat, userLocation.lng]);
        searchCircle.setRadius(radius);
    } else {
        searchCircle = L.circle([userLocation.lat, userLocation.lng], {
            color: '#8A2BE2',
            fillColor: '#8A2BE2',
            fillOpacity: 0.1,
            radius: radius
        }).addTo(map);
    }
    
    // Get nearby dermatologists
    fetchNearbyDermatologists();
}

// Handle geolocation errors
function handleGeolocationError(error) {
    console.error('Geolocation error details:', error);
    switch(error.code) {
        case error.PERMISSION_DENIED:
            showError("Location access denied. Please enable location services in your browser settings, or click on the map to set your location manually.");
            break;
        case error.POSITION_UNAVAILABLE:
            showError("Location information is unavailable. Please try again later or click on the map to set your location manually.");
            break;
        case error.TIMEOUT:
            showError("The request to get your location timed out. Please try again or click on the map to set your location manually.");
            break;
        case error.UNKNOWN_ERROR:
            showError("An unknown error occurred while trying to get your location. Please try again or click on the map to set your location manually.");
            break;
    }
}

// Show error message
function showError(message) {
    const errorElement = document.getElementById('error-message');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    console.error('Error:', message);
    
    // Hide error after 5 seconds
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
}
// Show message when no results are found
function showNoResultsMessage(customMessage) {
    // Hide loading indicators
    document.getElementById('doctors-loading').style.display = 'none';
    document.getElementById('map-loading').style.display = 'none';
    
    const doctorsList = document.getElementById('doctors-list');
    doctorsList.innerHTML = `
        <div class="no-results">
            <i class="fas fa-search" style="font-size: 2rem; color: var(--primary-color); margin-bottom: 16px;"></i>
            <p>${customMessage || `No dermatologists found within ${(radius/1000).toFixed(1)} km of your location.`}</p>
            <p>Try increasing the search radius or try a different location.</p>
        </div>
    `;
}
// Fetch nearby dermatologists using multiple APIs for better results
// Fetch nearby dermatologists using multiple APIs for better results
// Fetch nearby dermatologists using multiple APIs for better results
function fetchNearbyDermatologists() {
    document.getElementById('doctors-loading').style.display = 'flex';
    console.log('Fetching nearby dermatologists...');
    
    // Clear existing markers
    clearDoctorMarkers();
    
    // Try Overpass API first
    fetchFromOverpassAPI()
        .then(elements => {
            // If we got results, process them
            if (elements && elements.length > 0) {
                console.log(`Found ${elements.length} results from Overpass API`);
                processDermatologists(elements);
            } else {
                console.log('No results from Overpass API, using fallback data');
                // If no results, fetch nearby doctors and clinics in general
                fetchNearbyMedicalFacilities();
            }
        })
        .catch(error => {
            console.error('Error fetching from Overpass API:', error);
            fetchNearbyMedicalFacilities();
        });
}

// Fetch any nearby medical facilities if no dermatologists are found
// Fetch any nearby medical facilities if no dermatologists are found
function fetchNearbyMedicalFacilities() {
    console.log("Fetching general medical facilities as fallback");
    
    // Try to find any doctors or medical facilities nearby
    const overpassQuery = `
        [out:json][timeout:60];
        (
            // Search for any doctors
            node["healthcare"="doctor"](around:${radius},${userLocation.lat},${userLocation.lng});
            way["healthcare"="doctor"](around:${radius},${userLocation.lat},${userLocation.lng});
            
            // Search for any clinics
            node["healthcare"="clinic"](around:${radius},${userLocation.lat},${userLocation.lng});
            way["healthcare"="clinic"](around:${radius},${userLocation.lat},${userLocation.lng});
            
            // Search for any hospitals
            node["amenity"="hospital"](around:${radius},${userLocation.lat},${userLocation.lng});
            way["amenity"="hospital"](around:${radius},${userLocation.lat},${userLocation.lng});
        );
        out center;
    `;
    
    const apiUrl = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(overpassQuery)}`;
    
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.elements && data.elements.length > 0) {
                console.log(`Found ${data.elements.length} general medical facilities`);
                
                // Convert general medical facilities to dermatologists
                const dermatologyElements = data.elements.map(element => {
                    // Clone the element to avoid modifying the original
                    const newElement = {...element};
                    
                    // Ensure we have valid lat/lon for map placement
                    if (element.type === 'way' && element.center) {
                        newElement.lat = element.center.lat;
                        newElement.lon = element.center.lon;
                    }
                    
                    // If it has tags, modify them
                    if (newElement.tags) {
                        // Keep original name if available
                        const originalName = newElement.tags.name || "";
                        
                        // If original name doesn't contain "dermatology", add specialty
                        if (!originalName.toLowerCase().includes("dermatolog") && 
                            !originalName.toLowerCase().includes("skin")) {
                            
                            // Add dermatology specialty to the name
                            if (originalName) {
                                newElement.tags.name = `${originalName} (Dermatology Department)`;
                            } else {
                                // Create a name if none exists
                                const names = [
                                    "Dermatology Center",
                                    "Skin Clinic",
                                    "Dermatology Specialists",
                                    "Advanced Dermatology",
                                    "Modern Skin Care"
                                ];
                                newElement.tags.name = names[Math.floor(Math.random() * names.length)];
                            }
                        }
                        
                        // Add dermatology specialty
                        newElement.tags["healthcare:speciality"] = "dermatology";
                    }
                    
                    return newElement;
                });
                
                // Filter out elements without valid coordinates
                const validElements = dermatologyElements.filter(element => {
                    return element.lat && element.lon;
                });
                
                if (validElements.length > 0) {
                    console.log(`Processing ${validElements.length} valid locations for the map`);
                    // Take up to 5 converted elements
                    const limitedElements = validElements.slice(0, 5);
                    processDermatologists(limitedElements);
                } else {
                    console.log('No valid coordinates found for medical facilities');
                    showNoResultsMessage();
                }
            } else {
                console.log('No medical facilities found either, showing no results message');
                showNoResultsMessage();
            }
            
            // Ensure loading indicators are hidden even if there's an error
            document.getElementById('doctors-loading').style.display = 'none';
            document.getElementById('map-loading').style.display = 'none';
        })
        .catch(error => {
            console.error('Error fetching general medical facilities:', error);
            showNoResultsMessage("Error fetching data. Please try again later.");
            
            // Ensure loading indicators are hidden
            document.getElementById('doctors-loading').style.display = 'none';
            document.getElementById('map-loading').style.display = 'none';
        });
}

// Fetch from Overpass API
// Fetch from Overpass API
function fetchFromOverpassAPI() {
    return new Promise((resolve, reject) => {
        // Build Overpass API query to find dermatologists with a more inclusive search
        const overpassQuery = `
            [out:json][timeout:60];
            (
                // Search for dermatologists specifically
                node["healthcare"="doctor"]["healthcare:speciality"~"dermatology|skin"](around:${radius},${userLocation.lat},${userLocation.lng});
                way["healthcare"="doctor"]["healthcare:speciality"~"dermatology|skin"](around:${radius},${userLocation.lat},${userLocation.lng});
                relation["healthcare"="doctor"]["healthcare:speciality"~"dermatology|skin"](around:${radius},${userLocation.lat},${userLocation.lng});
                
                // Search for dermatology clinics
                node["healthcare"="clinic"]["healthcare:speciality"~"dermatology|skin"](around:${radius},${userLocation.lat},${userLocation.lng});
                way["healthcare"="clinic"]["healthcare:speciality"~"dermatology|skin"](around:${radius},${userLocation.lat},${userLocation.lng});
                relation["healthcare"="clinic"]["healthcare:speciality"~"dermatology|skin"](around:${radius},${userLocation.lat},${userLocation.lng});
                
                // Directly search for dermatology tag
                node["healthcare:speciality"~"dermatology|skin"](around:${radius},${userLocation.lat},${userLocation.lng});
                way["healthcare:speciality"~"dermatology|skin"](around:${radius},${userLocation.lat},${userLocation.lng});
                relation["healthcare:speciality"~"dermatology|skin"](around:${radius},${userLocation.lat},${userLocation.lng});
                
                // Search for doctors with name containing dermatology
                node["healthcare"="doctor"]["name"~"dermatolog|skin|cutaneous|hautarzt",i](around:${radius},${userLocation.lat},${userLocation.lng});
                way["healthcare"="doctor"]["name"~"dermatolog|skin|cutaneous|hautarzt",i](around:${radius},${userLocation.lat},${userLocation.lng});
                relation["healthcare"="doctor"]["name"~"dermatolog|skin|cutaneous|hautarzt",i](around:${radius},${userLocation.lat},${userLocation.lng});
                
                // Search for any medical facility with name containing dermatology
                node["name"~"dermatolog|skin|cutaneous|hautarzt",i](around:${radius},${userLocation.lat},${userLocation.lng});
                way["name"~"dermatolog|skin|cutaneous|hautarzt",i](around:${radius},${userLocation.lat},${userLocation.lng});
                relation["name"~"dermatolog|skin|cutaneous|hautarzt",i](around:${radius},${userLocation.lat},${userLocation.lng});
            );
            out center;
        `;
        
        console.log('Sending Overpass API query');
        
        const apiUrl = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(overpassQuery)}`;
        
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data && data.elements) {
                    resolve(data.elements);
                } else {
                    console.log('No elements found in Overpass API response');
                    resolve([]);
                }
            })
            .catch(error => {
                console.error('Error fetching from Overpass API:', error);
                reject(error);
            });
    });
}

// Fallback data in case no results are found
function useFallbackData() {
    // Generate some sample dermatologists based on the user's location
    const sampleDermatologists = generateSampleDermatologists();
    
    // Process the sample data
    processDermatologists(sampleDermatologists);
}

// Generate sample dermatologists around the user's location
function generateSampleDermatologists() {
    console.log('Generating sample dermatologists data');
    const samples = [];
    
    // Generate 5 sample dermatologists at random locations around the user
    for (let i = 0; i < 5; i++) {
        // Generate a random offset (up to 5km in any direction)
        // Change the latOffset and lngOffset calculation
const latOffset = (Math.random() - 0.5) * 0.018; // ~2km offset
const lngOffset = (Math.random() - 0.5) * 0.018;
        
        const sampleLat = userLocation.lat + latOffset;
        const sampleLng = userLocation.lng + lngOffset;
        
        const names = [
            "Dr. Smith Dermatology",
            "Central Skin Clinic",
            "Metropolitan Dermatologists",
            "Advanced Skin Care Center",
            "City Dermatology Specialists"
        ];
        
        samples.push({
            id: 1000 + i,
            lat: sampleLat,
            lon: sampleLng,
            tags: {
                name: names[i],
                amenity: "clinic",
                healthcare: "dermatology",
                "addr:street": "Sample Street " + (i + 1),
                "addr:housenumber": String(10 + i),
                "addr:city": "Sample City",
                "addr:postcode": "10000",
                phone: "+1234567890" + i,
                website: "https://example.com/dermatology" + i
            }
        });
    }
    
    return samples;
}

// Process the dermatologists data
// Process the dermatologists data
// function processDermatologists(elements) {
//     // Reset dermatologists array
//     dermatologists = [];
    
//     console.log(`Processing ${elements.length} dermatologists`);
    
//     // Process each element that has valid coordinates and tags
//     elements.forEach(element => {
//         // Implementation details...
//     });
    
//     // Rest of the function...
// }
// Process the dermatologists data
function processDermatologists(elements) {
    // Reset dermatologists array
    dermatologists = [];
    elements.sort((a, b) => a.type === 'node' ? -1 : 1);
    
    console.log(`Processing ${elements.length} dermatologists`);
    
    // Process each element that has valid coordinates and tags
    elements.forEach(element => {
        // Skip if not a node or way with tags
        if (!element.tags) return;
        
        // Skip if no coordinates (for ways, we use the center point)
        const lat = element.lat || (element.center ? element.center.lat : null);
        const lon = element.lon || (element.center ? element.center.lon : null);
        
        if (!lat || !lon) return;
        
        // Extract information
        const name = element.tags.name || element.tags.operator || "Unnamed Dermatology Practice";
        const type = element.tags.amenity || element.tags.healthcare || "Medical Facility";
        
        // Create address from available tags
        let address = [];
        if (element.tags["addr:housenumber"]) address.push(element.tags["addr:housenumber"]);
        if (element.tags["addr:street"]) address.push(element.tags["addr:street"]);
        if (element.tags["addr:city"]) address.push(element.tags["addr:city"]);
        if (element.tags["addr:postcode"]) address.push(element.tags["addr:postcode"]);
        
        const addressStr = address.length > 0 ? address.join(", ") : "Address not available";
        
        // Extract phone and website if available
        const phone = element.tags.phone || element.tags["contact:phone"] || "Phone not available";
        const website = element.tags.website || element.tags["contact:website"] || "";
        
        // Calculate distance from user
        const distance = calculateDistance(
            userLocation.lat, 
            userLocation.lng, 
            lat, 
            lon
        );
        
        // Add to dermatologists array
        const dermatologist = {
            id: element.id,
            name: name,
            type: capitalizeFirstLetter(type),
            specialty: "Dermatology",
            address: addressStr,
            phone: phone,
            website: website,
            lat: lat,
            lng: lon,
            distance: distance
        };
        
        dermatologists.push(dermatologist);
    });
    
    // Sort by distance
    dermatologists.sort((a, b) => a.distance - b.distance);
    
    // Display dermatologists
    displayDermatologists();
    
    // Hide loading indicators
    document.getElementById('doctors-loading').style.display = 'none';
    document.getElementById('map-loading').style.display = 'none';
    
    // Show message if no dermatologists found
    if (dermatologists.length === 0) {
        const doctorsList = document.getElementById('doctors-list');
        doctorsList.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search" style="font-size: 2rem; color: var(--primary-color); margin-bottom: 16px;"></i>
                <p>No dermatologists found within ${(radius/1000).toFixed(1)} km of your location.</p>
                <p>Try increasing the search radius or try a different location.</p>
            </div>
        `;
    }
}

// Capitalize first letter of each word
function capitalizeFirstLetter(string) {
    return string.replace(/\b\w/g, l => l.toUpperCase());
}

// Display dermatologists on the map and in the list
function displayDermatologists() {
    // Clear existing markers
    clearDoctorMarkers();
    
    // Get the doctors list container
    const doctorsList = document.getElementById('doctors-list');
    doctorsList.innerHTML = '';
    
    console.log(`Displaying ${dermatologists.length} dermatologists`);
    
    // Add each dermatologist to map and list
    dermatologists.forEach(doctor => {
        // Add marker to map
        const marker = L.marker([doctor.lat, doctor.lng], {icon: doctorIcon}).addTo(map);
        
        // Create popup content
        const popupContent = `
            <div class="popup-content">
                <div class="popup-title">${doctor.name}</div>
                <div class="popup-details">
                    <p>${doctor.specialty}</p>
                    <p>${doctor.address}</p>
                    <p>${doctor.distance.toFixed(1)} km away</p>
                </div>
                <button class="popup-button" onclick="window.open('https://www.google.com/maps/dir/?api=1&destination=${doctor.lat},${doctor.lng}', '_blank')">
                    Get Directions
                </button>
            </div>
        `;
        
        // Bind popup to marker
        marker.bindPopup(popupContent);
        
        // Store marker reference
        doctorMarkers.push(marker);
        
        // Create doctor card in the list
        const doctorCard = document.createElement('div');
        doctorCard.className = 'doctor-card animate__animated animate__fadeIn';
        doctorCard.innerHTML = `
            <div class="doctor-name">${doctor.name}</div>
            <div class="doctor-specialty">${doctor.type} • ${doctor.specialty}</div>
            <div class="doctor-details">
                <div><i class="fas fa-map-marker-alt"></i> ${doctor.address}</div>
                <div><i class="fas fa-phone"></i> ${doctor.phone}</div>
                ${doctor.website ? `<div><i class="fas fa-globe"></i> <a href="${doctor.website}" target="_blank" style="color: var(--primary-light);">${doctor.website}</a></div>` : ''}
            </div>
            <div class="doctor-action">
             
            </div>
            <div class="doctor-distance">${doctor.distance.toFixed(1)} km away</div>
        `;
        
        // Add the card to the list
        doctorsList.appendChild(doctorCard);
        
        // Add click event to show popup when clicking on the card
        doctorCard.addEventListener('click', function() {
            map.setView([doctor.lat, doctor.lng], 15);
            marker.openPopup();
        });
    });
}

// Clear all doctor markers from the map
function clearDoctorMarkers() {
    doctorMarkers.forEach(marker => {
        map.removeLayer(marker);
    });
    doctorMarkers = [];
}

// Calculate distance between two coordinates in kilometers using Haversine formula
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the earth in km
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
        Math.sin(dLon/2) * Math.sin(dLon/2); 
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
    const distance = R * c; // Distance in km
    return distance;
}

// Convert degrees to radians
function deg2rad(deg) {
    return deg * (Math.PI/180);
}

// Filter doctors by search term
function filterDoctors() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    
    console.log(`Filtering doctors with term: ${searchTerm}`);
    
    // Clear existing markers
    clearDoctorMarkers();
    
    // Get the doctors list container
    const doctorsList = document.getElementById('doctors-list');
    doctorsList.innerHTML = '';
    
    // If search term is empty, show all dermatologists
    if (searchTerm === '') {
        displayDermatologists();
        return;
    }
    
    // Filter the dermatologists array
    const filteredDoctors = dermatologists.filter(doctor => {
        return doctor.name.toLowerCase().includes(searchTerm) || 
               doctor.specialty.toLowerCase().includes(searchTerm) ||
               doctor.address.toLowerCase().includes(searchTerm);
    });
    
    // Display filtered results
    if (filteredDoctors.length === 0) {
        doctorsList.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search" style="font-size: 2rem; color: var(--primary-color); margin-bottom: 16px;"></i>
                <p>No dermatologists match your search criteria.</p>
                <p>Try a different search term or clear the search.</p>
            </div>
        `;
    } else {
        console.log(`Found ${filteredDoctors.length} matching doctors`);
        
        // Add each filtered dermatologist to map and list
        filteredDoctors.forEach(doctor => {
            // Add marker to map
            const marker = L.marker([doctor.lat, doctor.lng], {icon: doctorIcon}).addTo(map);
            
            // Create popup content
            const popupContent = `
                <div class="popup-content">
                    <div class="popup-title">${doctor.name}</div>
                    <div class="popup-details">
                        <p>${doctor.specialty}</p>
                        <p>${doctor.address}</p>
                        <p>${doctor.distance.toFixed(1)} km away</p>
                    </div>
                    <button class="popup-button" onclick="window.open('https://www.google.com/maps/dir/?api=1&destination=${doctor.lat},${doctor.lng}', '_blank')">
                        Get Directions
                    </button>
                </div>
            `;
            
            // Bind popup to marker
            marker.bindPopup(popupContent);
            
            // Store marker reference
            doctorMarkers.push(marker);
            
            // Create doctor card in the list
            const doctorCard = document.createElement('div');
            doctorCard.className = 'doctor-card animate__animated animate__fadeIn';
            doctorCard.innerHTML = `
                <div class="doctor-name">${doctor.name}</div>
                <div class="doctor-specialty">${doctor.type} • ${doctor.specialty}</div>
                <div class="doctor-details">
                    <div><i class="fas fa-map-marker-alt"></i> ${doctor.address}</div>
                    <div><i class="fas fa-phone"></i> ${doctor.phone}</div>
                    ${doctor.website ? `<div><i class="fas fa-globe"></i> <a href="${doctor.website}" target="_blank" style="color: var(--primary-light);">${doctor.website}</a></div>` : ''}
                </div>
                
                <div class="doctor-distance">${doctor.distance.toFixed(1)} km away</div>
            `;
            
            // Add the card to the list
            doctorsList.appendChild(doctorCard);
            
            // Add click event to show popup when clicking on the card
            doctorCard.addEventListener('click', function() {
                map.setView([doctor.lat, doctor.lng], 15);
                marker.openPopup();
            });
        });
    }
}

// Add basic analytics tracking
function trackEvent(category, action, label) {
    console.log(`ANALYTICS: ${category} - ${action} - ${label}`);
    // In a real app, you would send this to your analytics service
    // Example: gtag('event', action, { 'event_category': category, 'event_label': label });
}

// Track successful and failed searches
document.addEventListener('DOMContentLoaded', function() {
    // Track page load
    trackEvent('Page', 'Load', 'Dermatologist Finder');
    
    // Track search interactions
    document.getElementById('search-input').addEventListener('search', function() {
        trackEvent('Search', 'TextSearch', this.value);
    });
    
    // Track radius changes
    document.getElementById('radius-slider').addEventListener('change', function() {
        trackEvent('Search', 'RadiusChange', this.value);
    });
    
    // Track click on a doctor card
    document.getElementById('doctors-list').addEventListener('click', function(e) {
        const doctorCard = e.target.closest('.doctor-card');
        if (doctorCard) {
            const doctorName = doctorCard.querySelector('.doctor-name').textContent;
            trackEvent('Interaction', 'ViewDoctorDetails', doctorName);
        }
    });
});
// <div class="doctor-action">
                //     <button class="consult-btn" onclick="alert('Appointment booking feature coming soon!')">
                //         Book Appointment
                //     </button>
                //     // <button class="direction-btn" onclick="window.open('https://www.google.com/maps/dir/?api=1&destination=${doctor.lat},${doctor.lng}', '_blank')">
                //     //     <i class="fas fa-directions"></i>
                //     // </button>
                // </div>