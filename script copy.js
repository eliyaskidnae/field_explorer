// Initialize map
const map = L.map('map').setView([46.603354, 1.888334], 5); // Centered on France
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);
let parsedGeoJSON;
let geojsonData;

let features = [];
async function loadGeoJSON() {
    try {
        const response = await fetch('/data');
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        let partialData = ''; 
        let done = false;

        while (!done) {
            const { done: streamDone, value } = await reader.read();
            done = streamDone;
            if (value) {
                partialData += decoder.decode(value, { stream: true });
                try {
                    const parsedData = JSON.parse(partialData);
                    partialData = ''; 
                    if (parsedData.features) {
                        features = features.concat(parsedData.features);
                    }
                } catch (error) {
                    continue;
                }
            }
        }

        populateDropdown();
    } catch (error) {
        console.error('Error loading GeoJSON data:', error);
    }
}

async function populateDropdown() {
    try {
        let codeCultuData;

        // Check if data is available in localStorage
        const storedData = localStorage.getItem('codeCultuData');
        if (storedData) {
            codeCultuData = JSON.parse(storedData);
            console.log('Data loaded from localStorage');
        } else {
            // Fetch data from the server
            const response = await fetch('/data');
            codeCultuData = await response.json();
            // Save data to localStorage
            localStorage.setItem('codeCultuData', JSON.stringify(codeCultuData));
            console.log('Data fetched from server and saved to localStorage');
        }

        const codeCultuSelect = document.getElementById('codeCultu');
        codeCultuSelect.innerHTML = ''; 

        Object.keys(codeCultuData).forEach(key => {
            const option = document.createElement('option');
            option.value = codeCultuData[key];
            option.textContent = codeCultuData[key];
            codeCultuSelect.appendChild(option);
        });

        $('#codeCultu').select2({
            placeholder: "Select a code cultu", 
            allowClear: true 
        });
    } catch (error) {
        console.error('Error fetching codeCultu data:', error);
    }
}

// Call the function to populate the dropdown when the page loads
populateDropdown();

loadGeoJSON();

// Create a layer group to manage markers and polygons
const layerGroup = L.layerGroup().addTo(map);

async function filterData() {
    const codeCultuValue = document.getElementById('codeCultu').value;
    const surfaceHaValue_min = document.getElementById('surfaceHa_min').value;
    const surfaceHaValue_max = document.getElementById('surfaceHa_max').value;

    const response = await fetch('/filter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            codeCultu: codeCultuValue,
            surfaceHa_max: surfaceHaValue_max,
            surfaceHa_min: surfaceHaValue_min,
        })
    });

    const geojson = await response.json();
    const results = geojson.filtered_features.features;
    const lt_1 = geojson.features_lt_1;
    const bn_1_3 = geojson.features_1_to_3;
    const bn_3_8 = geojson.features_3_to_8;
    const gt_8 = geojson.features_gt_8;
    const total_area = geojson.total_features;
    const all_features  = geojson.all_features;

    document.getElementById('lt_1').textContent = lt_1;
    document.getElementById('bn_1_3').textContent = bn_1_3;
    document.getElementById('bn_3_8').textContent = bn_3_8;
    document.getElementById('gt_8').textContent = gt_8;
    document.getElementById('total_area').textContent =`${total_area} / ${all_features}` ;
    // document.getElementById('all_features').innerHTML 
    document.getElementById('resultList').innerHTML = ''; 
    console.log(`${results.length} results received`);

    // Clear the layer group
    layerGroup.clearLayers();

    results.forEach(feature => {
        const listItem = document.createElement('li');
        listItem.textContent = `${feature.properties.lbl_commun}, Surface: ${feature.properties.surface_ha}`;

        listItem.addEventListener('click', () => {
            const coordinates = feature.geometry.coordinates[0]; 
            if (Array.isArray(coordinates) && coordinates.length > 0) {
                const leafletCoordinates = coordinates.map(coord => [coord[1], coord[0]]);
                L.polygon(leafletCoordinates, {
                    color: 'blue',
                    weight: 3,
                    fillColor: 'blue',
                    fillOpacity: 0.2
                }).addTo(layerGroup);

                //marker
                const center = getPolygonCenter(coordinates);
                const [lat, lon] = center; 
                map.setView([lat, lon], 19);
                // L.marker(center).addTo(layerGroup).bindPopup(feature.properties.lbl_commun).openPopup();
                const marker = L.marker(center).addTo(layerGroup).bindPopup(feature.properties.lbl_commun);//.openPopup();

                // Add click event listener to the marker
                marker.on('click', () => {
                    console.log('Marker clicked');
                    map.setView([lat, lon], 19);
                });
            } else {
                console.error("Invalid coordinates for polygon.");
            }
        });
        document.getElementById('resultList').appendChild(listItem);
    });

// Add markers for each feature
results.forEach(feature => {
    const geometry = feature.geometry;
    let coordinates = [];

    if (geometry.type === 'Polygon') {
        coordinates = geometry.coordinates[0];
    } else if (geometry.type === 'MultiPolygon') {
        coordinates = geometry.coordinates[0][0];
    }

    if (Array.isArray(coordinates) && coordinates.length > 0) {
        const leafletCoordinates = coordinates.map(coord => [coord[1], coord[0]]);
        L.polygon(leafletCoordinates, {
            color: 'blue',
            weight: 3,
            fillColor: 'blue',
            fillOpacity: 0.05
        }).addTo(layerGroup);

        const center = getPolygonCenter(coordinates);
        const marker = L.marker(center).addTo(layerGroup).bindPopup(feature.properties.lbl_commun).openPopup();

        // Add click event listener to the marker
        marker.on('click', () => {
            map.setView(center, 19);
        });
    } else {
        console.error("Invalid coordinates for polygon.");
    }
});
}

function getPolygonCenter(coordinates) {
    let latSum = 0, lonSum = 0, numPoints = coordinates.length;
    coordinates.forEach(coord => {
        lonSum += coord[0];
        latSum += coord[1];
    });
    return [latSum / numPoints, lonSum / numPoints];
}


// Event listener for filter button
document.getElementById('filterButton').addEventListener('click', filterData);
