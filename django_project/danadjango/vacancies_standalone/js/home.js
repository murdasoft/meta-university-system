(function () {
  function esc(s) {
    if (s == null) return '';
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  document.addEventListener('DOMContentLoaded', function () {
    var D = window.JOB_PORTAL_DATA;
    if (!D) return;
    var meta = D.categoryMeta;
    var vacancies = D.vacancies || [];
    var F = window.JobPortalFilters;

    document.getElementById('vacancy-total').textContent = String(vacancies.length);
    document.getElementById('category-count').textContent = String(Object.keys(meta).length);

    var chips = document.getElementById('category-chips');
    if (chips) {
      var rows = F.categoryRows(meta, vacancies);
      chips.innerHTML = rows
        .map(function (c) {
          var empty = c.count ? '' : ' mock-chip--empty';
          return (
            '<a class="mock-chip mock-chip--sector' +
            empty +
            '" style="--chip-accent: ' +
            esc(c.color) +
            ';" href="vacancies.html?cat=' +
            encodeURIComponent(c.key) +
            '">' +
            '<span class="mock-chip__label">' +
            esc(c.label) +
            '</span>' +
            '<span class="mock-chip__count">' +
            c.count +
            '</span></a>'
          );
        })
        .join('');
    }

    var list = document.getElementById('latest-jobs');
    if (list) {
      var top = F.sortByPostedDesc(vacancies).slice(0, 8);
      list.innerHTML = top
        .map(function (job) {
          return (
            '<a href="vacancy.html#' +
            encodeURIComponent(job.slug) +
            '" class="mock-job-card mock-job-card--rich" style="--card-accent: ' +
            esc(job.accent_color) +
            ';">' +
            '<div class="mock-job-card__row">' +
            '<span class="mock-job-card__sector">' +
            esc(job.cat_label) +
            '</span>' +
            '<time class="mock-job-card__date">' +
            esc(job.posted) +
            '</time></div>' +
            '<p class="mock-job-card__title">' +
            esc(job.title) +
            '</p>' +
            '<p class="mock-job-card__meta">' +
            esc(job.company) +
            ' · ' +
            esc(job.city) +
            ' · ' +
            esc(job.salary) +
            '</p>' +
            '<p class="mock-job-card__foot">' +
            esc(job.format) +
            ' · ' +
            esc(job.employment) +
            '</p></a>'
          );
        })
        .join('');
    }

    var dl = document.getElementById('mock-cities-home');
    if (dl) {
      dl.innerHTML = F.uniqueCities(vacancies)
        .map(function (city) {
          return '<option value="' + esc(city) + '">';
        })
        .join('');
    }
  });
})();
