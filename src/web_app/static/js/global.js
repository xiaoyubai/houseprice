$(function() {

	$('#criteria').collapse('hide');
	$('#filters').collapse('hide');
	$('#location').collapse('hide');

	$('#mapModal, #streetModal').modal({
		backdrop: true,
		show: false
		}).css({
		width: '651px',
		height: '470px',
		'margin-left': function () {
			return -($(this).width() / 2);
		}
	});

	// Setup drop down menu
	$('.dropdown-toggle').dropdown();

	// Fix input element click problem
	$('.dropdown-menu input, .dropdown-menu label').click(function(e) {
		e.stopPropagation();
	});


	if($('#carousel-home').length == 1) {
		$('#carousel-loader').hide();
		$('.showcase').show();
		$("#carousel").awShowcase(
		{
			content_width:			'100%',
			content_height:			326,
			fit_to_parent:			false,
			auto:					true,
			interval:				3000,
			continuous:				true,
			loading:				true,
			tooltip_width:			200,
			tooltip_icon_width:		32,
			tooltip_icon_height:	32,
			tooltip_offsetx:		18,
			tooltip_offsety:		0,
			arrows:					true,
			buttons:				false,
			btn_numbers:			false,
			keybord_keys:			true,
			mousetrace:				false, /* Trace x and y coordinates for the mouse */
			pauseonover:			true,
			stoponclick:			true,
			transition:				'hslide', /* hslide/vslide/fade */
			transition_delay:		300,
			transition_speed:		500,
			show_caption:			'show', /* onload/onhover/show */
			thumbnails:				false,
			thumbnails_position:	'outside-last', /* outside-last/outside-first/inside-last/inside-first */
			thumbnails_direction:	'horizontal', /* vertical/horizontal */
			thumbnails_slidex:		0, /* 0 = auto / 1 = slide one thumbnail / 2 = slide two thumbnails / etc. */
			dynamic_height:			false, /* For dynamic height to work in webkit you need to set the width and height of js/jquery.aw-showcase/images in the source. Usually works to only set the dimension of the first slide in the showcase. */
			speed_change:			true, /* Set to true to prevent users from swithing more then one slide at once. */
			viewline:				false /* If set to true content_width, thumbnails, transition and dynamic_height will be disabled. As for dynamic height you need to set the width and height of js/jquery.aw-showcase/images in the source. */
		});

		$("#carousel-home").hover(
			function () {
				$('.showcase-arrow-previous, .showcase-arrow-next').fadeIn();
			},
			function () {
				$('.showcase-arrow-previous, .showcase-arrow-next').fadeOut();
			}
		);



	}

	if($('#showcase-loader').length == 1) {
		$('#showcase-loader').hide();
		$('#owl-demo').show();
		$('#owl-thumbnails').show();
		 $("#owl-demo").owlCarousel({

		navigation : false, // Show next and prev buttons
		slideSpeed : 300,
		paginationSpeed : 400,
		singleItem:true,
		pagination:false,
		autoPlay: true
		});


 var owl = $("#owl-gallery");

owl.owlCarousel({


		pagination:false,
		 items : 4
		// "singleItem:true" is a shortcut for:
		// items : 1,
		// itemsDesktop : false,
		// itemsDesktopSmall : false,
		// itemsTablet: false,
		// itemsMobile : false

		});

	// Custom Navigation Events
	$("#owl-gallery a").click(function(){
		owl_goTo($(this).data('slide'));
	})
	$(".owl-next").click(function(){
		owl.trigger('owl.next');
	})
	$(".owl-prev").click(function(){
		owl.trigger('owl.prev');
	})
	}


	$('.property_sold').badger('Just sold');
	$('.premium_property').eq(0).badger('new home');
	$('.premium_property').eq(1).badger('under offer');
	$('.premium_property').eq(2).badger('special offer');

	//theme switcher
    $('#theme_switcher ul li a').bind('click',
        function(e) {
            $("#switch_style").attr("href", "css/"+$(this).data('theme')+".css");
            return false;
        }
    );

	Response.ready(responsive_actions)  // call fn on ready
	Response.ready(responsive_large)  // call fn on ready
	Response.resize(responsive_actions) // call fn on resize



});

function owl_goTo(x) {
	var owl = $("#owl-demo").data('owlCarousel');
	owl.goTo(x);
}


var home_map;
function initializeHomeMap() {
	if($('#home_map_canvas').length == 0)
		return;
	var myOptions = {
		zoom: 5,
		center: new google.maps.LatLng(37.75,-122.44),
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		draggable: false,
		disableDoubleClickZoom: false,
		zoomControl: false,
		overviewMapControl: false,
		streetViewControl: false,
		mapTypeControl: false,
		scrollwheel: false,
		disableDefaultUI: false
	};
	home_map = new google.maps.Map(document.getElementById('home_map_canvas'), myOptions);
	google.maps.event.addListener(home_map, 'click', function() {
		window.location.href = "map_properties.html";
	});

}

google.maps.event.addDomListener(window, 'load', initializeHomeMap);


var map;
function initializePropertiesMap() {
	if($('#map_canvas').length == 0)
		return;
	var myLatlng = new google.maps.LatLng(37.75,-122.44);
	var myOptions = {
		zoom: 13,
		center: myLatlng,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	}
	var infowindow = new google.maps.InfoWindow();
	var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	$.each(map_locations, function(key, value) {
		var marker = new google.maps.Marker({
			position: new google.maps.LatLng(value['lat'], value['lng']),
			map: map,
			icon: 'static/css/images/marker.png',
			scrollwheel: false,
			streetViewControl:true,
			title: value['title'],
            price: value['price'],
            sqft: value['sqft'],
			img: value['img'],
			link: value['link']
		});

		var link = "link";
		google.maps.event.addListener( marker, 'click', function() {
			// Setting the content of the InfoWindow
			// var content = '<div id="info" class="span5"><div class="row">' + '<div class="span2"><img src="' + value['img'] + '" class="thumbnail" style="width:135px"/></div>' + '<div class="span3"><h6>' + value['price'] + '</h6>' + '<strong>&pound;' + value['sqft'] + '</strong>' + '<p><a href="' + value['link'] + '">More details >></a></p>' + '</div></div></div>';
			// infowindow.setContent(content );
			infowindow.open(map, marker);
		});

	});


}

google.maps.event.addDomListener(window, 'load', initializePropertiesMap);



function responsive_large() {

    if ( Response.band(768) )
    {
        // 768+
		if($('#people_viewing').length > 0) {
			setTimeout(function(){$.sticky($('#people_viewing').html())},3000);
		}

		if($('#contact_agent').length > 0) {
			$('#contact_agent').css('width', $('#contact_agent').width());
			$('#contact_agent').portamento();
		}
    }
    else
    {
        // 0->768
    }

}

function responsive_common() {
	$('#criteria').collapse('show');
	$('#filters').collapse('show');
	$('#location').collapse('show');
	$('.lform').height($("#carousel-home").height()-40);

}
function responsive_actions () {
	if ( Response.band(1200) )
    {
       // 1200+
		responsive_common()
    }
    else if ( Response.band(992) )
    {
        // 992+
		responsive_common()
    }
    else if ( Response.band(768) )
    {
        // 768+
		responsive_common()
    }
    else
    {
        // 0->768
		setTimeout(function() {
			$('#criteria').collapse('hide');
			$('#filters').collapse('hide');
			$('#location').collapse('hide');
			$('.lform').height('auto');
		}, 500);

    }
}
