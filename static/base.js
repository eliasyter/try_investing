const menu = document.querySelector('#mobile-menu')
const menuLinks = document.querySelector('.navbar__menu')

const home_link = document.querySelector('#home-page')
const about_link = document.querySelector('#about-page')
const services_link = document.querySelector('#services-page')

// display mobile menu

const mobileMenu=()=>{
    menu.classList.toggle('is-active')
    menuLinks.classList.toggle('active')
}

menu.addEventListener('click',mobileMenu)

