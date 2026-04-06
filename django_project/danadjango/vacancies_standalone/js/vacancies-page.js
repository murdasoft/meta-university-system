(function () {
  function esc(s) {
    if (s == null) return '';
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function qs(name) {
    var u = new URLSearchParams(window.location.search);
    return u.get(name) || '';
  }

  function buildQuery(preserve) {
    var p = new URLSearchParams();
    if (preserve.q) p.set('q', preserve.q);
    if (preserve.city) p.set('city', preserve.city);
    if (preserve.cat) p.set('cat', preserve.cat);
    if (preserve.fmt) p.set('fmt', preserve.fmt);
    if (preserve.emp) p.set('emp', preserve.emp);
    var s = p.toString();
    return s ? '?' + s : '';
  }

  document.addEventListener('DOMContentLoaded', function () {
    var D = window.JOB_PORTAL_DATA;
    if (!D) return;
    var meta = D.categoryMeta;
    var all = D.vacancies || [];
    var F = window.JobPortalFilters;

    var filters = {
      q: qs('q'),
      city: qs('city'),
      cat: qs('cat'),
      fmt: qs('fmt'),
      emp: qs('emp'),
    };

    document.getElementById('f-q').value = filters.q;
    document.getElementById('f-city').value = filters.city;
    document.getElementById('f-fmt').value = filters.fmt;
    document.getElementById('f-emp').value = filters.emp;

    var datalist = document.getElementById('mock-cities-list');
    if (datalist) {
      datalist.innerHTML = F.uniqueCities(all)
        .map(function (city) {
          return '<option value="' + esc(city) + '">';
        })
        .join('');
    }

    var rows = F.categoryRows(meta, all);
    var pills = document.getElementById('quick-pills');
    if (pills) {
      var base = buildQuery(filters);
      pills.innerHTML =
        '<a href="vacancies.html" class="mock-pill' +
        (!filters.cat ? ' is-active' : '') +
        '">Все сферы</a>' +
        rows
          .filter(function (c) {
            return c.count > 0;
          })
          .map(function (c) {
            var next = Object.assign({}, filters, { cat: c.key });
            var hq = buildQuery(next);
            return (
              '<a href="vacancies.html' +
              hq +
              '" class="mock-pill' +
              (filters.cat === c.key ? ' is-active' : '') +
              '" style="--pill-accent: ' +
              esc(c.color) +
              ';">' +
              esc(c.label) +
              ' <span class="mock-pill__n">' +
              c.count +
              '</span></a>'
            );
          })
          .join('');
    }

    var sel = document.getElementById('f-cat');
    if (sel) {
      sel.innerHTML =
        '<option value="">Все (' + all.length + ')</option>' +
        rows
          .filter(function (c) {
            return c.count > 0;
          })
          .map(function (c) {
            return (
              '<option value="' +
              esc(c.key) +
              '"' +
              (filters.cat === c.key ? ' selected' : '') +
              '>' +
              esc(c.label) +
              ' (' +
              c.count +
              ')</option>'
            );
          })
          .join('');
    }

    var filtered = F.sortByPostedDesc(
      F.filterVacancies(all, filters.q, filters.city, filters.cat, filters.fmt, filters.emp),
    );

    document.getElementById('catalog-total').textContent = String(all.length);
    document.getElementById('filtered-count').textContent = String(filtered.length);
    document.getElementById('filtered-wrap').style.display =
      filtered.length !== all.length ? 'inline' : 'none';

    var container = document.getElementById('vacancies-list');
    if (!container) return;
    if (!filtered.length) {
      container.innerHTML =
        '<p class="mock-empty">По таким условиям ничего не нашлось — <a href="vacancies.html">сбросьте фильтры</a>.</p>';
      return;
    }
    container.innerHTML =
      '<div class="mock-job-list mock-job-list--spaced">' +
      filtered
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
            '</p>' +
            '<p class="mock-job-card__salary">' +
            esc(job.salary) +
            '</p>' +
            '<p class="mock-job-card__tags">' +
            (job.tags || [])
              .map(function (t) {
                return '<span class="mock-tag">' + esc(t) + '</span>';
              })
              .join('') +
            '</p>' +
            '<p class="mock-job-card__foot">' +
            esc(job.format) +
            ' · ' +
            esc(job.employment) +
            '</p></a>'
          );
        })
        .join('') +
      '</div>';
  });
})();
