$(function(){
	
	//step object to pause a slide 5% of the way in
	var pauseFivePCIn = {
		5: function(e, b){
			this.pause();
		}
	},
		body = $('body');
	
	//handler for theme switching
	var themeSwap = function(theme){
		body.removeClass('jtour-white').removeClass('jtour-black').removeClass('jtour-yellow').removeClass('jtour-blue').addClass('jtour-'+theme);
	}
	
	$.jTour({
		tourId:				'spotlight',
		pages:				[
			{url: 'index.html', items: [
				{
					sel:		'.section.spotlight img',
					title:		'jTour Interactive Demo: Spotlight',
					msg:		'<p>Welcome to the jTour Spotlight demo! In this tour, you will see how jTour\'s Spotlight feature can draw a user\'s attention. What\'s even better is that you can use it on any element, not just the one that the tour is positioned relative to. Let\'s get started...</p>',
					elemPos:	'tr',
					boxPos:		'tl',
					scrollTop:	-120,
					offsetLeft: 60,
					delay:		3000,
					steps:{
						5: function(e, b){
							this.pause();
						}
					}
				},
				{
					sel:		'.section.spotlight img',
					msg:		'<p>And here is the spotlight!</p>',
					elemPos:	'tr',
					boxPos:		'tl',
					scrollTop:	-120,
					offsetLeft: 60,
					delay:		3000,
					onStart:	function(e, b){
							this.spotlight();
							this.pause();
					}
				},
				{
					sel:		'.section.spotlight img',
					msg:		'<p>Not let\'s try it on the image above ^^</p>',
					elemPos:	'tr',
					boxPos:		'tl',
					scrollTop:	-120,
					offsetLeft: 60,
					delay:		3000,
					onStart:	function(e, b){
							this.spotlight({element: $('.section:eq(2) img')});
							this.pause();
					}
				},
				{
					sel:		'.section.spotlight img',
					title:		'jTour Interactive Demo: Spotlight',
					msg:		'<p>As you can see, jTour\'s Spotlight feature is both powerful and functional. Remember, you can apply the spotlight effect to any element on the page, not just the one that the tour item is positioned relative to.</p>',
					elemPos:	'tr',
					boxPos:		'tl',
					scrollTop:	-120,
					offsetLeft: 60,
					delay:		3000,
					onStart:	function(e, b){
							this.pause();
					}
				},
			]}
		]
			
	});
	
	
	$.jTour({
		tourId:				'multi',
		pages:				[
			{url: 'index.html', items: [
				{
					sel:		'.section.multi',
					title:		'jTour Interactive Demo: Multipage',
					msg:		'<p>Welcome to the jTour multipage tour demo! In this tour, you will see first hand just how powerful jTour is in being able to take your users on tours across multiple different pages. Let\'s get started...</p>',
					elemPos:	't',
					boxPos:		't',
					scrollTop:	-120,
					delay:		3000,
					steps:{
						5: function(e, b){
							this.pause();
						}
					}
				}
			]}, 
			{url: 'page2.html', items: [
				{
					sel:		'body',
					msg:		'<p>As you can see, we have now moved to another page and jTour is still guiding us through the tour. Let\'s go back to the first page.</p>',
					elemPos:	't',
					boxPos:		't',
					scrollTop:	-120,
					offsetTop:	120,
					delay:		12000,
				}
			]}, 
			{url: 'index.html', items: [
				{
					sel:		'.section.multi',
					title:		'jTour Interactive Demo: Multipage',
					msg:		'<p>Thanks for taking the multipage tour demo. jTour is a powerful tour engine. It can handle anything - even multipage tours!</p>',
					elemPos:	't',
					boxPos:		't',
					delay:		1000,
					scrollTop:	-120,
					steps:{
						5: function(e, b){
							this.pause();
						}
					}
				}
			]}
		]
			
	});

	
	
	$.jTour({
		tourId:				'themes',
		onTourClose:		function(e, b){
								themeSwap('white');
		},
		pages:				[
			{url: '', items: [
				{
					sel:		'.section.themes',
					title:		'jTour Interactive Demo: Themes',
					msg:		'<p>Welcome to the jTour themes demo! In this tour, you will be able to see each theme in action, on the fly. This is the default theme (white). Let\'s get started...</p>',
					elemPos:	't',
					boxPos:		't',
					delay:		10000,
					steps: {
						5: function(e, b){
							this.pause();
							this.spotlight($('.section').eq(1));
						}
					}
				},
				{
					sel:		'.section.themes',
					title:		'Black Theme',
					msg:		'<p>This is the black theme.</p>',
					elemPos:	't',
					boxPos:		't',
					delay:		1000,
					onStart:	function(e, b){
						themeSwap('black');
					},
					steps:{
						5: function(e, b){
							this.pause();
						}
					}
				},
				{
					sel:		'.section.themes',
					title:		'Yellow Theme',
					msg:		'<p>This is the yellow theme.</p>',
					elemPos:	't',
					boxPos:		't',
					delay:		1000,
					onStart:	function(e, b){
						themeSwap('yellow');
					},
					steps:{
						5: function(e, b){
							this.pause();
						}
					}
				},
				{
					sel:		'.section.themes',
					title:		'Blue Theme',
					msg:		'<p>This is the blue theme.</p>',
					elemPos:	't',
					boxPos:		't',
					delay:		1000,
					onStart:	function(e, b){
						themeSwap('blue');
					},
					steps:{
						5: function(e, b){
							this.pause();
						}
					}
				},
				{
					sel:		'.section.themes',
					title:		'jTour Interactive Demo: Themes',
					msg:		'<p>Thanks for watching!</p>',
					elemPos:	't',
					boxPos:		't',
					delay:		1000,
					onStart:	function(e, b){
						themeSwap('white');
					},
					steps:{
						5: function(e, b){
							this.pause();
						}
					}
				}
			]}
		]
			
	});

	
	
	$.jTour({
		tourId:				'smartscroll',
		pages:				[
			{url: '', items: [
				{
					sel:		'.section.scrolling',
					title:		'jTour Interactive Demo: Scrolling',
					msg:		'<p>Welcome to the jTour smart scrolling demo! In this short tour, you will see how jTour can intelligently scroll to the exact position that you need.</p><p>Let\'s get started by taking a look at some dumb scrolling</p>',
					elemPos:	't',
					boxPos:		't',
					scrollTop:	-120,
					offsetTop:	-200,
					delay:		6000,
					steps:{
						5: function(e, b){
							this.pause();
						}
					}
				},
				{
					sel:		'.section.scrolling',
					msg:		'<p>As you can see, jTour has scrolled until the tour box is visible at the top of the viewport. But let\'s try some smart scrolling...</p>',
					elemPos:	't',
					boxPos:		't',
					offsetTop:	900,
					delay:		2500
				},
				{
					sel:		'.section.scrolling',
					msg:		'<p>As you can see, by using the offsetTop property (a similar one exists for horizontal scrolling offsets: scrollLeft), jTour can now scroll intelligently so that our tour ends up precisely where we want it. In this example, the scrolling stopped 120px above the top of the tour box, by setting scrollTop to -120</p>',
					elemPos:	't',
					boxPos:		't',
					scrollTop:	-120,
					offsetTop:	-30,
					delay:		6000,
					steps:{
						5: function(e, b){
							this.pause();
						}
					}
				},
				{
					sel:		'.section.scrolling',
					title:		'jTour Interactive Demo: Scrolling',
					msg:		'<p>While jTour will allow simple scrolling, it is also intelligent enough to offer smart scrolling capabilities, so that your tour items are placed exactly where you want. Think of smart scrolling like padding/margins for the viewport.</p>',
					elemPos:	't',
					boxPos:		't',
					scrollTop:	-120,
					offsetTop:	-30,
					delay:		4000,
					steps:{
						5: function(e, b){
							this.pause();
						}
					}
				}
			]}
		]
			
	});

	$.jTour({
		tourId:				'pos',
		pages: [
			{url: '', items: [
				{
					sel:		'.section.positions',
					title:		'jTour Interactive Demo: Positioning',
					msg:		'<p>Welcome to the jTour positioning demo! In this short tour, you will see how to position the tour boxes relative to an element. In fact, there are 81 different ways to position them, and when you include offsets it becomes limitless.</p><p>Feel free to use the controls to rewind, skip, etc., or just hover over the box to pause temporarily.</p><p>Let\'s get started...</p>',
					elemPos:	't',
					boxPos:		't',
					scrollTop:	-120,
					offsetTop:	120,
					delay:		6000,
					steps:{
						5: function(e, b){
							this.pause();
						}
					}
				},
				{
					sel:		'.pd',
					msg:		'<p>A quick example: This box has it\'s Bottom-Right corner pinned to the element\'s Bottom-Right.</p>',
					delay:		3000,
					elemPos:	'br',
					boxPos:		'br',
					steps:		pauseFivePCIn
				},
				{
					sel:		'.pd',
					msg:		'<p>For the purposes of this demo, all the boxes are aligned to the image in the centre.</p><p>This is the default positioning: The top left corner of the box is aligned to the bottom left corner of the element.</p>',
					delay:		5000
				},
				{
					sel:		'.pd',
					msg:		'<p>You can choose from 1 of 9 positions on the element (in this case the .pd tag) to align the tour box to. This is Top-Left. This reflects the elemPos property of the tour item. For top left, set the elemPos to \'tl\'</p>',
					delay:		2500,
					elemPos:	'tl',
					steps:		pauseFivePCIn
				},
				{
					sel:		'.pd',
					msg:		'<p>Top-Centre; elemPos:\'t\'</p>',
					delay:		1000,
					elemPos:	't'
				},
				{
					sel:		'.pd',
					msg:		'<p>Top-Right; elemPos:\'tr\'</p>',
					delay:		1000,
					elemPos:	'tr'
				},
				{
					sel:		'.pd',
					msg:		'<p>Centre-Left; elemPos:\'l\' or \'lc\'</p>',
					delay:		1000,
					elemPos:	'l'
				},
				{
					sel:		'.pd',
					msg:		'<p>Centre-Centre; elemPos:\'c\' or \'cc\'</p>',
					delay:		1000,
					elemPos:	'c'
				},
				{
					sel:		'.pd',
					msg:		'<p>Centre-Right; elemPos:\'r\' or \'rc\'</p>',
					delay:		1000,
					elemPos:	'r'
				},
				{
					sel:		'.pd',
					msg:		'<p>Bottom-Left; elemPos:\'bl\'</p>',
					delay:		1000,
					elemPos:	'bl'
				},
				{
					sel:		'.pd',
					msg:		'<p>Bottom-Centre; elemPos:\'b\'</p>',
					delay:		1000,
					elemPos:	'b'
				},
				{
					sel:		'.pd',
					msg:		'<p>Bottom-Right; elemPos:\'br\'</p>',
					delay:		1000,
					elemPos:	'br'
				},
				{
					sel:		'.pd',
					msg:		'<p>Accordingly, you can also choose from 1 of 9 positions to use as the anchor the tour box. These boxes are all pinned to the vertical and horizontal centre of the image element. This box has its Top-Left corner anchored to the image\'s Centre-Centre point; boxPos: \'tl\', elemPos: \'cc\'</p>',
					delay:		5000,
					elemPos:	'cc',
					boxPos:		'tl',
					steps:		pauseFivePCIn
				},
				{
					sel:		'.pd',
					msg:		'<p>Top-Centre; boxPos:\'t\'</p>',
					delay:		1000,
					elemPos:	'cc',
					boxPos:		't'
				},
				{
					sel:		'.pd',
					msg:		'<p>Top-Right; boxPos:\'tr\'</p>',
					delay:		1000,
					elemPos:	'cc',
					boxPos:		'tr'
				},
				{
					sel:		'.pd',
					msg:		'<p>Centre-Left; boxPos:\'l\' or \'lc\'</p>',
					delay:		1000,
					elemPos:	'cc',
					boxPos:		'l'
				},
				{
					sel:		'.pd',
					msg:		'<p>Centre-Centre; boxPos:\'c\' or \'cc\'</p>',
					delay:		1000,
					elemPos:	'cc',
					boxPos:		'c'
				},
				{
					sel:		'.pd',
					msg:		'<p>Centre-Right; boxPos:\'r\' or \'rc\'</p>',
					delay:		1000,
					elemPos:	'cc',
					boxPos:		'r'
				},
				{
					sel:		'.pd',
					msg:		'<p>Bottom-Left; boxPos:\'bl\'</p>',
					delay:		1000,
					elemPos:	'cc',
					boxPos:		'bl'
				},
				{
					sel:		'.pd',
					msg:		'<p>Bottom-Centre; boxPos:\'b\'</p>',
					delay:		1000,
					elemPos:	'cc',
					boxPos:		'b'
				},
				{
					sel:		'.pd',
					msg:		'<p>Bottom-Right; boxPos:\'br\'</p>',
					delay:		1000,
					elemPos:	'cc',
					boxPos:		'br'
				},
				{
					sel:		'.pd',
					msg:		'<p>We can take this even further by adding a horizontal and/or vertical offset. For this box, the offset is the default of 0,0. These values must be entered as numbers and represent the number of pixels by which to offset the box.</p>',
					delay:		3000,
					elemPos:	'tl',
					boxPos:		'tl',
					steps:		pauseFivePCIn
				},
				{
					sel:		'.pd',
					msg:		'<p>What about an offset of 80px from the left & 50 from the top? offsetLeft: 80, offsetTop, 50</p>',
					delay:		2000,
					elemPos:	'tl',
					boxPos:		'tl',
					offsetTop:	50,
					offsetLeft:	80
				},
				{
					sel:		'.pd',
					msg:		'<p>60px from the left & 100 from the top? offsetLeft: 60, offsetTop, 100</p>',
					delay:		1500,
					elemPos:	'tl',
					boxPos:		'tl',
					offsetTop:	100,
					offsetLeft:	60
				},
				{
					sel:		'.pd',
					msg:		'<p>-40px from the left & -40 from the top? offsetLeft: -40, offsetTop, -40</p>',
					delay:		1500,
					elemPos:	'tl',
					boxPos:		'tl',
					offsetTop:	-40,
					offsetLeft:	-40
				},
				{
					sel:		'.section.positions',
					title:		'jTour Interactive Demo: Positioning',
					msg:		'<p>So as you can see, with over 81 ways to position the tour boxes relative to their respective element, jTour is not only super easy to use, but incredibly capable as well.</p><p>It\'s your tour, and you can position an element anywhere you want!</p>',
					elemPos:	't',
					boxPos:		't',
					scrollTop:	-120,
					offsetTop:	120,
					delay:		10000
				}		
				
			]}
		]
	});
});