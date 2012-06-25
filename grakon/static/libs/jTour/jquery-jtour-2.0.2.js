/*
 * jTour Multipage Website Tour 2.0.2
 * http://benmartinstudios.com/
 *
 * Copyright 2012, Ben Martin
 * Must not be used without permission
 * Contact ben.martin@benmartinstudios.com for more details
 *
*/

(function($){

	function fitInRange(num, min, max){
		return Math.min(Math.max(min, num), max);
	}

	function isInRange(num, min, max){
		return (num>=min && num<=max);
	}

	var body	= $('body'),
		jWin	= $(window),
		html	= $('html'),
	
		jTourOpts 	= {},
		jTours 		= {};
	
	jTourOpts.destroyTour = function(stng, intr, onComplete){
	
		intr.isDestroyed = true;
		intr.isTrans = false;
		intr.isPaused = false;
		
		//stop the timer
		intr.tourBox.timer.stop(true, false);
		
		//hide the overlay, the holder, and the tourbox and then remove it
		intr.overlay.add(intr.holder).fadeOut(stng.fadeTime, function() {
			$(this).remove();
		});
		
		//get rid of any spotlighting
		jTourOpts.unSpotlight();
		
		//when the tourbox is hidden, call the onComplete event
		intr.tourBox.tourBox.fadeOut(stng.fadeTime, function() {
			$(this).remove();
			if(typeof onComplete === 'function'){
				onComplete.call(intr.inst);
			}
			//**CB**
			//call the callback for onTourClose
			stng.onTourClose.call(intr.inst);
		});
		
		//remove any hash tag
		window.location.hash = '_';
	}
	
	jTourOpts.unSpotlight = function(){
		$('.jt-spotlit').removeClass('jt-spotlit');
	}
	
	jTourOpts.loadPage = function(stng, intr, pageNum, itemNum){
		//get the url to load
		var url = stng.pages[pageNum].url;
		//the format of a hash tag is #jTour/tourId/pageId/itemId
		window.location = url+'#jTour/'+stng.tourId+'/'+pageNum+'/'+((typeof item !== 'undefined') ? item : '0');
	}
	
	jTourOpts.parseHashTag = function(stng, intr){
		var hash = window.location.hash;
		if(hash.substring(1, 6) !== 'jTour'){ return false; }
		return hash.substring(7).split('/');
	}
	
	jTourOpts.parsePosition = function(p){
		return {
			h:	(p.indexOf('l') >= 0) ? -1 : (p.indexOf('r') >= 0) ? 1 : 0,
			v:	(p.indexOf('t') >= 0) ? -1 : (p.indexOf('b') >= 0) ? 1 : 0
		};
	}
	
	//function to test whether element is in viewport
	jTourOpts.isInViewport = function(elem){
		elem.fadeTo(0, 0.01);
		var minX = jWin.scrollLeft(),
			maxX = minX + jWin.width(),
			minY = jWin.scrollTop(),
			maxY = minY + jWin.height(),
			eOff = elem.offset(),
			test = {x: false, y: false};
		
		//test if in horizontal viewport
		if(isInRange(eOff.left, minX, maxX) && isInRange(eOff.left+elem.width(), minX, maxX)){
			test.x = true;
		}
		//test if in vertical viewport
		if(isInRange(eOff.top, minY, maxY) && isInRange(eOff.top+elem.height(), minY, maxY)){
			test.y = true;
		}
		return test;
	}
	
	jTourOpts.loadItem = function(stng, intr, item, start){
		var tB = intr.tourBox;
		
		if(typeof start !== 'boolean'){
			start = true;
		}
	
		//fill the tourbox with content
		var page = stng.pages[intr.currentPage].items[item];
		intr.page = page;
		
		page.elemO = page.elem.offset();
		
		if(typeof page.title !== 'undefined'){
			tB.heading.text(page.title).show();
		} else {
			tB.heading.hide();
		}
		tB.message.html(page.msg);
		tB.timer.width('0%');
	
		//position the tourbox, ensuring it stays on the page		
		var leftOffset	= 0.5*(page.elemPos.h+1)*page.elem.width()  - 0.5*(page.boxPos.h+1)*tB.tourBox.width(),
			topOffset	= 0.5*(page.elemPos.v+1)*page.elem.height() - 0.5*(page.boxPos.v+1)*tB.tourBox.height(),
			newLeft		= page.elemO.left + leftOffset + page.offsetLeft,
			newTop		= page.elemO.top  + topOffset  + page.offsetTop;
			
		if(stng.keepOnPage){
		
			//fit newLeft in range of 0<=newLeft>=(bodyWidth-tourBoxWidth)
			newLeft = fitInRange(newLeft, 0, Math.max(body.width(),  jWin.width())  - tB.tourBox.width());
			newTop  = fitInRange(newTop , 0, Math.max(body.height(), jWin.height()) - tB.tourBox.height());
		
		}
		
		tB.tourBox.css('top', 		newTop)
					.css('left',	newLeft);		
		
		
		//scroll to the new location, regardless of whether it is inside the viewport or not
		var isIn = jTourOpts.isInViewport(tB.tourBox);
		if(isIn.x && isIn.y){
			//scroll none
			showBox(stng, intr, page, tB, start);
		} else {
			var scrollO = {scrollLeft: body.scrollLeft(), scrollTop: body.scrollTop()};
			if(!isIn.y){
				//scroll y
				scrollO.scrollTop = newTop + page.scrollTop;
			}
			if(!isIn.x){
				//scroll x
				scrollO.scrollLeft = newLeft + page.scrollLeft;
			}
			body.add(html).animate(scrollO, {
				duration: stng.scrollTime,
				complete: function(){
					showBox(stng, intr, page, tB, start);
				}
			});
		}
		
		
	}
	
	function showBox(stng, intr, page, tB, start){
	
		intr.isTrans = false;
		
		if(typeof start !== 'boolean'){
			start = true;
		}
			
		tB.tourBox.fadeTo(stng.fadeTime,1);
		
		//**CB**
		//run the onStart callback if necessary
		if(typeof page.onStart === 'function'){
			page.onStart.call(intr.inst, page.elem, intr.tourBox.tourBox);
		}
		
		if(!intr.isPaused){
			jTourOpts.resumeTimer(stng, intr, page, tB);
		}
		
		if(intr.pauseOnHover){		
			tB.tourBox.hover(function(ev){
				intr.inst.pause();
			}, function(ev){
				intr.inst.resume();
			});
		}
		
	}
	
	jTourOpts.transition = function(stng, intr, page, item){
	
		if(intr.isTrans){
			//there is already a transition going on, so quit early
			return false;
		}
		intr.isTrans = true;
	
		//transitioning
	
		//stop the timer
		intr.tourBox.timer.stop(true, true);
		
		//get rid of any spotlighting
		jTourOpts.unSpotlight();
	
		var itemTo = item;
		if(item === '+' || item === 'next'){
			itemTo = intr.currentItem+1;
		} else if (item === '-' || item === 'previous'){
			itemTo = intr.currentItem-1;
		}
		
		intr.currentItem = itemTo;
		
		//fade the tourbox out
		intr.tourBox.tourBox.fadeOut(stng.fadeTim, function(){
		
			//check to see if page exists
			if(isInRange(itemTo, 0, stng.pages[intr.currentPage].items.length-1)){
				jTourOpts.loadItem(stng, intr, itemTo);
			} else {
				//test if it was under or over
				if(itemTo === -1){
					//under; go to previous page
					if(intr.currentPage === 0){
						jTourOpts.destroyTour(stng, intr);
					} else {
						jTourOpts.loadPage(stng, intr, intr.currentPage-1);
					}
				} else {
					//over; go to next page
					if(intr.currentPage === stng.pages.length-1){
						jTourOpts.destroyTour(stng, intr);
					} else {
						jTourOpts.loadPage(stng, intr, intr.currentPage+1);
					}
				}
			}
		});
		
	}
	
	jTourOpts.resumeTimer = function(stng, intr, page, tB){
	
		if(intr.isDestroyed){
			return;
		}
		
		//if there are any definite pauses (a pause for a specific time), clear them
		clearTimeout(intr.delay);
		
		intr.tourBox.controls.find('a.play-pause').removeClass('paused');
	
		//copy the steps
		if(typeof page.steps === 'object'){
			var stepsCopy = {};
			$.each(page.steps, function(ind, val){
				stepsCopy[ind] = 'step';
			});
		}
		
		//get current width to determine how long we should animate for
		var percent = parseFloat(tB.timer[0].style.width, 10)/100;
		tB.timer.width((percent*100 + 1)+'%');
		
		//start the timer
		tB.timer.animate({
			width: '100%'
		}, {
			duration: 	page.delay*(1-percent),
			complete: 	function(){
				//remove the hover listeners
				tB.tourBox.unbind('mouseenter mouseleave');
				//remove any jt-spotlit classes
				jTourOpts.unSpotlight();
				//**CB**
				//run the onComplete callback if necessary
				if(typeof page.onComplete === 'function'){
					page.onComplete.call(intr.inst, page.elem, intr.tourBox.tourBox);
				}
				jTourOpts.transition(stng, intr, page, '+');
			},
			step:		function(now, fx){
				//**CB**
				//call onStep if necessary
				if(typeof page.onStep === 'function'){
					page.onStep.call(intr.inst, page.elem, intr.tourBox.tourBox, now);
				}
				//call steps if necessary
				now = Math.round(now);
				//workaround to step callbacks being skipped at times
				var runFirst = false;
				if(typeof stepsCopy !== 'undefined'){
					$.each(stepsCopy, function(ind, val){
						if(parseInt(val, 10) >= now){
							runFirst = true;
						}
						return false;					
					});
					if(typeof stepsCopy[now] !== 'undefined' || runFirst){
						//**CB**
						page.steps[now].call(intr.inst, page.elem, intr.tourBox.tourBox);
						delete stepsCopy[now];
					}
					runFirst = false;
				}
			},
		});
	}
		
	//add listener for jTour links being clicked
	body.delegate('a.jtour', 'click', function(ev){
		//someone has initialized a tour from an anchor, so parse the tag and start the tour if need be
		var a = $(this).attr('href');
		if(a.substr(0,1)==='#'){
			window.location.hash = a;
			var tag = jTourOpts.parseHashTag(a)[0];
			if(typeof jTours[tag] !== 'undefined'){
				jTours[tag].init();
				ev.preventDefault();
			}
		}
	});

	var JTour = function(options, itemOptions){
	
		var init = function(){
		
			intr.isDestroyed = false;
			
			var tag = jTourOpts.parseHashTag(stng, intr);
			
			//set the current page/item
			//add +0 to allow parsing if value doesn't exist
			intr.currentPage = parseInt((typeof tag[1] !== 'undefined' ? tag[1] : 0), 10);
			intr.currentItem = parseInt((typeof tag[2] !== 'undefined' ? tag[2] : 0), 10);
		
			//if there is no jTour tag or the tourId does not match, do not start the tour
			if(!tag || tag[0] !== stng.tourId){
				return false;
			}
			
			//load the page
			jTourOpts.loadPage(stng, intr, intr.currentPage, intr.currentItem);
		
			//add the overlay
			body.append('<div class="jtour overlay"/>');
			intr.overlay = body.children('.jtour.overlay');
			
			//create the tour holder
			intr.holder = $('<div class="jtour holder"/>');
			
			if(intr.isMaiden){
			
				//loop through each item on this page and configure each slide
				$.each(stng.pages[intr.currentPage].items, function(ind, val){
					
					var itemSet 		= $.extend({}, itemstng, val);
						elem		 	= $(val.sel).first(),
						btn 			= $('<a class="jtour-btn" data-itemNum="'+val.num+' data-num="'+ind+'>'+val.num+'</a>'),
						elemO			= elem.offset();
					
					itemSet.elem = elem;
					itemSet.elemPos = jTourOpts.parsePosition(itemSet.elemPos);
					itemSet.boxPos = jTourOpts.parsePosition(itemSet.boxPos);
					
					stng.pages[intr.currentPage].items[ind] = itemSet;

				});
			
			}
			
			//create the tour box
			var tB = $('<div class="jtour box"/>'),
				main = $('<div class="jtour main"/>'),
				cntrls = $('<div class="jtour controls"/>');
				cntrls_ar = ['previous', 'play-pause', 'stop', 'next'];
				cntrls_ke = ['Previous Item: Up/Left Arrow', 'Play/Pause: Spacebar', 'Stop: Esc', 'Next Item: Right/Down Arrow'];
			main.append('<h1 class="jtour heading">jTour Demo</h1>')
				.append('<div class="message"><p>Lorem ipsum.</p></div>')
				.append('<div class="jtour timer"/>');
			
			//append each control
			for(i=0; i<4; i++){
				cntrls.append('<a class="jtour-ctrl '+cntrls_ar[i]+'" href="#'+cntrls_ar[i]+'" title="'+cntrls_ke[i]+'"/>');
			}			
		
			//if autoPlay is set to false, pause the tour and show the play button
			if(!stng.autoPlay){
				intr.isPaused = true;
				cntrls.find('.play-pause').addClass('paused');
			}
			
			main.append(cntrls);
			tB.append(main);
			
			//hide the tour box from display before attaching to dom
			tB.fadeTo(0, 0);
			
			//append the tour box to the holder		
			intr.holder.append(tB);
			intr.tourBox = {
				tourBox:	tB,
				heading:	tB.find('h1'),
				message:	tB.find('.message'),
				controls:	tB.find('.controls'),
				timer:		tB.find('.timer')		
			};
			
			//append the holder to the body
			body.append(intr.holder);
			
			
			
			//if stng.overlayCancel is true, allow the user to stop the tour by clicking the overlay ** actually it is the holder, but that is invisible
			if(stng.overlayCancel){
				intr.holder.click(function(ev){
					if($(ev.target).hasClass('holder')){
						jTourOpts.destroyTour(stng, intr);
					}
				});
			}
			
			if(intr.isMaiden){
			
				//add listener to save hover state
				tB.hover(function(ev){
					intr.isHovered = true;
				}, function(ev){
					intr.isHovered = false;
				});
				
				var ui = function(ev){
					if(!intr.isDestroyed){
						ev.preventDefault();
						var el = $(this),
							h = (ev.type === 'click') ? el.attr('href') : ev.keyCode+'';
							h = (ev.type === 'click') ? el.attr('href') : ev.keyCode+'';
						if(h.match(/#previous|37|38/)){
							//previous button, or left/up arrow
							jTourOpts.transition(stng, intr, intr.page, '-');
							ev.preventDefault();
						} else if(h.match(/#next|39|40/)){
							//next button, or right/down arrow
							jTourOpts.transition(stng, intr, intr.page, '+');
							ev.preventDefault();
						} else if (h.match(/#play-pause|32/)){
							//play-pause button, or spacebar
							intr.isHovered = true;
							if(!intr.isTrans){
								if(intr.isPaused){
									resume();
								} else {				
									pause();
								}
							}
							ev.preventDefault();
						} else if (h.match(/#stop|27/)){
							//stop button, or escape key
							//destroy the tour
							jTourOpts.destroyTour(stng, intr);
							ev.preventDefault();
						} else {
							return true;
						}
					}
				}
				
				//add listeners for control buttons
				body.delegate('a.jtour-ctrl', 'click', ui);
				
				//add listeners for keyboard
				body.keydown(ui);
			
			}
			
			//**CB**
			//call the callback for onTourOpen
			stng.onTourOpen.call(intr.inst);
			
			//start the tour!
			jTourOpts.loadItem(stng, intr, intr.currentItem, stng.autoPlay);
			
			intr.isMaiden = false;
		}
		
		var spotlight = function(opts){
			var page = stng.pages[intr.currentPage].items[intr.currentItem];
			if(typeof opts === 'undefined'){
				opts = {};
			}
			if(opts.unSpotlightAll){
				jTourOpts.unSpotlight();
			}
			if(typeof opts.element === 'undefined'){
				//if no el is defined, get the el for the current tour item
				opts.element = page.elem;
			} else {
				//make sure the element is a jQuery object first
				opts.element = $(opts.element);
			}
			opts.element.addClass('jt-spotlit');
		}
		
		this.spotlight = spotlight;
		this.unSpotlight = jTourOpts.unSpotlight;
	
		this.init = init;
	
		//default stng
		var stng = $.extend({
			tourId:				'tour',
			autoPlay:			true,
			fadeTime:			200,
			scrollTime:			600,
			overlayCancel:		true,
			pauseOnHover:		false,
			keepOnPage:			true,
			pages:				[],
			onTourOpen:			function(){},
			onTourClose:		function(){}
		}, options || {});
		
		var intr = {
			overlay: 		'',
			currentPage: 	0,
			currentItem:	0,
			timer:			'',
			isPaused:		false,
			isDestroyed:	true,
			isMaiden:		true,
			isTrans:		false,
			isHovered:		false,
			delay:			''
		};
		
		var itemstng = $.extend({
			elemPos: 		'bl',
			boxPos:			'tl',
			offsetTop:		0,
			offsetLeft:		0,
			scrollTop:		0,
			scrollLeft:		0,
			delay: 			5000
		}, itemOptions || {});
		
		intr.inst = this;
		jTours[stng.tourId] = this;
		
		//public functions
	
		var pause = function(delay){
			if(intr.isPaused || intr.isTrans){
				//return early if the tour is already playing or in the middle of a transition
				return false;
			}
			intr.tourBox.controls.find('a.play-pause').addClass('paused');
			intr.isPaused = true;
			intr.tourBox.timer.stop(true);
			if(typeof delay !== 'undefined'){
				intr.delay = setTimeout(resume, delay);
			}
		}
		
		var resume = function(){
			if(!intr.isPaused || intr.isTrans){
				//return early if the tour is already playing or in the middle of a transition
				return false;
			}
			intr.tourBox.controls.find('a.play-pause').removeClass('paused');
			intr.isPaused = false;
			jTourOpts.resumeTimer(stng, intr, intr.page, intr.tourBox);
		}
	
		var exit = function(){
			jTourOpts.destroyTour(stng, intr);
		}
	
		this.pause = pause;
		this.resume = resume;
		this.exit = exit;
		
		/* * * * * * * * * * * * * * *
		 * * * start the process * * *
		 * * * * * * * * * * * * * * */
		
		if(stng.pages.length > 0){
			//initialize the tour only if some pages exist
			init();
		}
		
	}

	$.jTour = $.fn.jTour = function(options, itemOptions) {
		//var element = $('html');
		//var elem = this;
		// Return early if this element already has a plugin instance
		//if (element.data('jTour')) return;
		// Pass options to plugin constructor
		var jTour = new JTour(options, itemOptions);
		// Store plugin object in this element's data
		//element.data('jTour', jTour);
		return jTour;
	};

})(jQuery);