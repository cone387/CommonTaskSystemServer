$(document).ready(function () {
  const $type = $('#id_type');
  const $crontab = $('.form-row.field-crontab');
  const $nextScheduleTime = $('.fieldBox.field-next_schedule_time');
  const $period = $('.fieldBox.field-period');
  const $timings = $('.form-row.field-timings_type');
  const $timings_time = $('.form-row.field-timing_time');
  const $weekdays = $('.form-row.field-weekdays');
  const $timing_type = $('#id_timings_type');

  function show_hide_weekdays(){
    const t = $timing_type.val();
    const $periodUnit = $('#id_period_unit');
    if(t === 'WEEKDAYS'){
      $weekdays.show();
      $periodUnit.text('周');
    }else{
      $weekdays.hide();
      $periodUnit.text('天');
    }
  }

  function show_hide_timings(show){
    if(show){
      $timings.show();
      $timings_time.show();
      show_hide_weekdays();
    }else{
      $timings.hide();
      $timings_time.hide();
      $weekdays.hide();
    }
  }

  function show_hide_fields() {
    console.log($type.val());
    const t = $type.val();
    if (t === 'C') {
      $crontab.show();
      $nextScheduleTime.hide();
      $period.hide();
    } else if (t === 'S') {
      $crontab.hide();
      $nextScheduleTime.show();
      $period.show();
    } else if (t === 'O') {
      $crontab.hide();
      $nextScheduleTime.show();
      $period.hide();
    }else if(t === 'T'){
      $crontab.hide();
      $nextScheduleTime.hide();
      $period.hide();
    }
    show_hide_timings(t === 'T');
  }
  show_hide_fields();
  $type.on('change', show_hide_fields);
  $timing_type.on('change', show_hide_weekdays);
});