// Get a reference to the input and button
const searchInput = document.getElementById('search-text');
const pageInput = document.getElementById('page');
const searchButton = document.getElementById('search-button');

// Read the parameters we used when the page loaded so we can pre-populate the search box with it
const parameters = new URLSearchParams(window.location.search);
searchInput.value = parameters.get('name')
page.value = parameters.get('page')
