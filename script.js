document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('theme-toggle-btn');
    const body = document.body;

    // Check for saved theme preference in localStorage
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        body.classList.toggle('light-theme', currentTheme === 'light');
    }

    toggleButton.addEventListener('click', () => {
        body.classList.toggle('light-theme');
        
        // Save theme preference in localStorage
        const theme = body.classList.contains('light-theme') ? 'light' : 'dark';
        localStorage.setItem('theme', theme);
    });

    function gotoindex(){
        window.location.href = './index.html';
    }

    function changeheading(query){
        console.log(window.location.href);
        const place = document.getElementById('splh3');
        if(place){
            place.textContent = 'Searching' + query;
        }
        else{
            console.log('Error: Element not found');
        }
    }
    
    var glob_query = ''
    const homeSearchButton = document.getElementById('home-search-button');
    const searchButton = document.getElementById('search-button');
    const homeSearchInput = document.querySelector('.search-bar');
    const searchInput = document.querySelector('.home-search-bar');
    if(homeSearchButton){
        homeSearchButton.addEventListener('click',()=>{
            var query = homeSearchButton.value;
            var glob_query = query;
            gotoindex();
            console.log('query',changeheading(query));
        })
    } 
    else if(searchButton){
        searchButton.addEventListener('click',()=>{
            const query = searchInput.value;
            changeheading(query);
        })
    }
    else{
        console.log(glob_query);
        console.log('eroor');
    }

});
