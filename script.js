document.addEventListener('DOMContentLoaded', function () {
  
  document.getElementById('dusche').addEventListener('change', filterWohnheime);
  document.getElementById('kueche').addEventListener('change', filterWohnheime);
  document.getElementById('moebliert').addEventListener('change', filterWohnheime);
  document.getElementById('barrierefrei').addEventListener('change', filterWohnheime);
  document.getElementById('wartezeit').addEventListener('change', filterWohnheime);
  document.getElementById('maxMietpreis').addEventListener('change', filterWohnheime);
  document.getElementById('minWohn').addEventListener('change', filterWohnheime);
  document.getElementById('personen').addEventListener('change', filterWohnheime);

  filterWohnheime();
});

function changeWidth(isMouseOver) {
	const filter = document.getElementById('filter');
	const map = document.getElementById('map');

	if (isMouseOver) {
		filter.style.width = '0%'; 
		map.style.width = '100%'; 
		impressum.style.width = '100%'; 
	} else {
		filter.style.width = '14%';
		map.style.width = '86%'; 
		impressum.style.width = '86%'; 
	}
}
