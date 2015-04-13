/**
 * @fileoverview Manager for signal slots throught the application.
 * Refer to this when creating new signals, and to connect slots.
 *
 * @author (cesarpalomo@gmail.com) Cesar Palomo
 */



/**
 * Manages signal slots for application UI.
 */
var SigSlots = (function() {
  ////// Signals definition is centralized here.
  __sig__.clusters_count_changed = function(clustersCount) {};
  __sig__.pages_labels_changed = function() {};
  __sig__.term_selected = function(term) {};
  __sig__.query_enter = function(query) {};
  __sig__.pages_do_ranking = function() {};
  __sig__.pages_extract_terms = function() {};
  __sig__.brushed_pages_changed = function(pagesIndices) {};
  __sig__.add_term_to_query_box = function(term) {};

  var pub = {};
  ////// CONNECTS SIGNALS TO SLOTS
  // e.g. SigSlots.connect(__sig__.eventHappened, myObject, myObject.onEventHappened);
  pub.connect = function(
      signal, slotInstance, slotMethod) {
    __sig__.connect(
      __sig__, signal,
      slotInstance, slotMethod);
  };
  return pub;
}());
