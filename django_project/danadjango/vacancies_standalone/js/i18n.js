/**
 * Интерфейс: русский по умолчанию, қазақ тілі (KK) по переключателю.
 * localStorage: jobPortalLang = ru | kk
 */
(function (global) {
  var LS_KEY = 'jobPortalLang';

  var STR = {
    ru: {
      'brand.name': 'Портал вакансий',

      'shell.login': 'Вход',
      'shell.register': 'Регистрация',
      'shell.logout': 'Выйти',
      'shell.cabinet': 'Кабинет',
      'shell.admin': 'Админ',

      'shell.langAria': 'Язык интерфейса',
      'shell.themeToDark': 'Тёмная тема',
      'shell.themeToLight': 'Светлая тема',
      'shell.themeAriaDark': 'Включить тёмное оформление',
      'shell.themeAriaLight': 'Включить светлое оформление',

      'footer.privacy': 'Политика конфиденциальности',
      'footer.offer': 'Публичная оферта',
      'footer.contacts': 'Контакты',
      'footer.social': 'Мы в соцсетях:',
      'footer.copy': ' Портал вакансий. Все права защищены.',

      'auth.login.docTitle': 'Вход — Портал вакансий',
      'auth.login.title': 'Вход в личный кабинет',
      'auth.login.lead':
        'Один вход для соискателей (физических лиц) и для представителей работодателей. Система откроет нужный кабинет автоматически.',
      'auth.login.tabSeeker': 'Соискатель',
      'auth.login.tabEmployer': 'Работодатель / партнёр',
      'auth.login.hintSeekerTitle': 'Если вы ищете работу',
      'auth.login.hintSeekerHtml':
        '<ul class="mock-auth-hint-list"><li>После входа доступны резюме, отклики, сохранённые вакансии и уведомления.</li><li>Логин и пароль вы задаёте при <a href="register.html">регистрации</a> как физическое лицо.</li><li>Данные для входа хранятся в вашем браузере до выхода из аккаунта.</li></ul>',
      'auth.login.hintEmployerTitle': 'Если вы нанимаете сотрудников',
      'auth.login.hintEmployerHtml':
        '<ul class="mock-auth-hint-list"><li>Кабинет работодателя: публикация вакансий, отклики, поиск резюме, настройки компании.</li><li>Учётную запись оформляет представитель ТОО, ИП или кадрового агентства (партнёра).</li><li>Используйте устойчивый пароль и корпоративную почту, указанную при регистрации.</li></ul>',
      'auth.login.labelLogin': 'Логин',
      'auth.login.labelPass': 'Пароль',
      'auth.login.phLogin': 'Введите логин',
      'auth.login.phPass': 'Введите пароль',
      'auth.login.submit': 'Войти',
      'auth.login.footer': 'Нет аккаунта?',
      'auth.login.footerLink': 'Регистрация',

      'auth.register.docTitle': 'Регистрация — Портал вакансий',
      'auth.register.title': 'Регистрация',
      'auth.register.leadHtml':
        'Выберите тип учётной записи. Нажимая «Зарегистрироваться», вы подтверждаете ознакомление с <a href="privacy.html">политикой конфиденциальности</a> и <a href="offer.html">публичной офертой</a>.',
      'auth.register.tabSeeker': 'Я соискатель (физлицо)',
      'auth.register.tabEmployer': 'Я работодатель или партнёр',
      'auth.register.hintSeekerTitle': 'Учётная запись соискателя',
      'auth.register.hintSeekerHtml':
        '<ul class="mock-auth-hint-list"><li>Подходит для граждан РК и иных лиц, ищущих работу по найму или проектно.</li><li>Укажите действующий e-mail — на него будут приходить ответы работодателей (после запуска рассылки).</li><li>Логин — короткое имя для входа (латиница или цифры, без пробелов).</li></ul>',
      'auth.register.hintEmployerTitle': 'Учётная запись организации',
      'auth.register.hintEmployerHtml':
        '<ul class="mock-auth-hint-list"><li>Для ТОО, ИП, филиалов и кадровых агентств (партнёров платформы).</li><li>Рекомендуем логин по сокращённому названию компании и рабочий e-mail ответственного лица.</li><li>БИН, юридический адрес и реквизиты можно будет добавить в разделе «Настройки компании» в кабинете.</li></ul>',
      'auth.register.labelLogin': 'Логин',
      'auth.register.labelEmail': 'E-mail',
      'auth.register.labelPass': 'Пароль (не менее 4 символов)',
      'auth.register.labelRole': 'Тип учётной записи',
      'auth.register.labelCompany': 'Название организации',
      'auth.register.phLoginSeeker': 'Например: ivan_ivanov',
      'auth.register.phLoginEmployer': 'Например: too_dana_hr',
      'auth.register.phEmail': 'name@company.kz',
      'auth.register.phCompany': 'ТОО «…», ИП Иванов, бренд клиники',
      'auth.register.helpCompany': 'Как будет отображаться в кабинете и в карточках вакансий. Если не заполнить — используется логин.',
      'auth.register.optCompany': 'Только для работодателя / партнёра',
      'auth.register.submit': 'Зарегистрироваться',
      'auth.register.footer': 'Уже зарегистрированы?',
      'auth.register.footerLink': 'Войти',
      'auth.register.roleSeeker': 'Соискатель (физическое лицо)',
      'auth.register.roleEmployer': 'Работодатель / партнёр (юрлицо или ИП)',

      'auth.err.shortUser': 'Логин не короче 2 символов.',
      'auth.err.shortPass': 'Пароль не короче 4 символов.',
      'auth.err.badLogin': 'Неверный логин или пароль.',
      'auth.err.taken': 'Этот логин недоступен. Укажите другой.',
      'auth.ok.welcome': 'Добро пожаловать, ',
      'auth.ok.register': 'Регистрация успешно завершена.',

      'dash.seeker.title': 'Личный кабинет соискателя',
      'dash.seeker.lead': 'Здравствуйте, ',
      'dash.seeker.leadEnd': ' Ниже отображается сводка по вашей активности на портале.',
      'dash.seeker.s1': 'Откликов',
      'dash.seeker.s2': 'Просмотров профиля',
      'dash.seeker.s3': 'Сохранённых вакансий',
      'dash.seeker.nextTitle': 'Что сделать дальше',
      'dash.seeker.n1': 'Заполните или обновите резюме — так работодатели быстрее найдут вас.',
      'dash.seeker.n2': 'Настройте уведомления о новых вакансиях по выбранным сферам и городам.',
      'dash.seeker.n3': 'Откликайтесь на подходящие предложения и отслеживайте статус в разделе «Мои отклики».',
      'dash.seeker.hint': 'Разделы слева откроют детальные экраны по мере подключения функционала.',
      'dash.seeker.link': 'Перейти к каталогу вакансий',
      'dash.seeker.nav1': 'Дашборд',
      'dash.seeker.nav2': 'Мои резюме',
      'dash.seeker.nav3': 'Мои отклики',
      'dash.seeker.nav4': 'Сохранённые вакансии',
      'dash.seeker.nav5': 'Настройки профиля',
      'dash.seeker.nav6': 'Уведомления',
      'dash.seeker.docTitle': 'Кабинет соискателя — Портал вакансий',

      'dash.employer.title': 'Личный кабинет работодателя',
      'dash.employer.lead': 'Организация: ',
      'dash.employer.leadEnd': ' Сводка по размещённым вакансиям и откликам кандидатов.',
      'dash.employer.s1': 'Активных вакансий',
      'dash.employer.s2': 'Новых откликов',
      'dash.employer.s3': 'Собеседований на неделе',
      'dash.employer.nextTitle': 'Рекомендации для партнёров и работодателей в РК',
      'dash.employer.n1': 'Проверьте реквизиты (БИН, юр. адрес) в настройках — они важны для доверия соискателей.',
      'dash.employer.n2': 'В описаниях вакансий указывайте формат работы, район города или удалённый формат явно.',
      'dash.employer.n3': 'Отвечайте на отклики в разумный срок — это повышает рейтинг компании на платформе.',
      'dash.employer.hint': 'Кабинет единообразен с интерфейсом соискателя для удобства обеих сторон.',
      'dash.employer.link': 'Открыть каталог вакансий',
      'dash.employer.nav1': 'Дашборд',
      'dash.employer.nav2': 'Мои вакансии',
      'dash.employer.nav3': 'Отклики на вакансии',
      'dash.employer.nav4': 'Поиск резюме',
      'dash.employer.nav5': 'Настройки компании',
      'dash.employer.nav6': 'Уведомления',
      'dash.employer.docTitle': 'Кабинет работодателя — Портал вакансий',
    },
    kk: {
      'brand.name': 'Бос орындар порталы',

      'shell.login': 'Кіру',
      'shell.register': 'Тіркелу',
      'shell.logout': 'Шығу',
      'shell.cabinet': 'Жеке кабинет',
      'shell.admin': 'Әкімші',

      'shell.langAria': 'Интерфейс тілі',
      'shell.themeToDark': 'Қараңғы тема',
      'shell.themeToLight': 'Жарық тема',
      'shell.themeAriaDark': 'Қараңғы көріністі қосу',
      'shell.themeAriaLight': 'Жарық көріністі қосу',

      'footer.privacy': 'Құпиялылық саясаты',
      'footer.offer': 'Қоғамдық оферта',
      'footer.contacts': 'Байланыс',
      'footer.social': 'Әлеуметтік желілер:',
      'footer.copy': ' Бос орындар порталы. Барлық құқықтар қорғалған.',

      'auth.login.docTitle': 'Кіру — Бос орындар порталы',
      'auth.login.title': 'Жеке кабинетке кіру',
      'auth.login.lead':
        'Бір кіру нүктесі: жұмыс іздеушілер (жеке тұлғалар) және жұмыс берушілердің өкілдері үшін. Жүйе сізге қажетті кабинетті өзі ашады.',
      'auth.login.tabSeeker': 'Жұмыс іздеуші',
      'auth.login.tabEmployer': 'Жұмыс беруші / серіктес',
      'auth.login.hintSeekerTitle': 'Егер сіз жұмыс іздесеңіз',
      'auth.login.hintSeekerHtml':
        '<ul class="mock-auth-hint-list"><li>Кіргеннен кейін түйіндеме, өтінімдер, сақталған бос орындар және хабарламалар қолжетімді болады.</li><li>Логин мен құпия сөзді жеке тұлға ретінде <a href="register.html">тіркелу</a> кезінде орнатасыз.</li><li>Кіру деректері шоттан шыққанға дейін браузеріңізде сақталады.</li></ul>',
      'auth.login.hintEmployerTitle': 'Егер сіз қызметкер жалдайтын болсаңыз',
      'auth.login.hintEmployerHtml':
        '<ul class="mock-auth-hint-list"><li>Жұмыс беруші кабинеті: бос орын жариялау, өтінімдер, түйіндеме іздеу, компания баптаулары.</li><li>Есептік жазбаны ЖШС, ЖК немесе кадрлық агенттік (серіктес) өкілі рәсімдейді.</li><li>Тіркеу кезінде көрсеткен корпоративтік поштаңызды және күрделі құпия сөзді пайдаланыңыз.</li></ul>',
      'auth.login.labelLogin': 'Логин',
      'auth.login.labelPass': 'Құпия сөз',
      'auth.login.phLogin': 'Логинді енгізіңіз',
      'auth.login.phPass': 'Құпия сөзді енгізіңіз',
      'auth.login.submit': 'Кіру',
      'auth.login.footer': 'Есептік жазба жоқ па?',
      'auth.login.footerLink': 'Тіркелу',

      'auth.register.docTitle': 'Тіркелу — Бос орындар порталы',
      'auth.register.title': 'Тіркелу',
      'auth.register.leadHtml':
        'Есептік жазба түрін таңдаңыз. «Тіркелу» батырмасын басу арқылы сіз <a href="privacy.html">құпиялылық саясатымен</a> және <a href="offer.html">қоғамдық оферта</a>мен танысқаныңызды растайсыз.',
      'auth.register.tabSeeker': 'Мен жұмыс іздеушімін (жеке тұлға)',
      'auth.register.tabEmployer': 'Мен жұмыс беруші немесе серіктеспін',
      'auth.register.hintSeekerTitle': 'Жұмыс іздеушінің есептік жазбасы',
      'auth.register.hintSeekerHtml':
        '<ul class="mock-auth-hint-list"><li>ҚР азаматтары және жалдамалы немесе жобалық жұмыс іздеушілер үшін.</li><li>Әрекетті e-mail көрсетіңіз — жұмыс берушілердің жауаптары осыға жіберіледі (хабарлама іске қосылғанда).</li><li>Логин — кіру үшін қысқа атау (латын әріптері немесе сандар, бос орынсыз).</li></ul>',
      'auth.register.hintEmployerTitle': 'Ұйымның есептік жазбасы',
      'auth.register.hintEmployerHtml':
        '<ul class="mock-auth-hint-list"><li>ЖШС, ЖК, филиалдар және кадрлық агенттіктер (платформа серіктестері) үшін.</li><li>Компанияның қысқартылған атауы бойынша логин және жауапты тұлғаның жұмыс поштасын ұсынамыз.</li><li>БСН, заңды мекенжай және деректемелерді кабинеттегі «Компания баптаулары» бөлімінде қосуға болады.</li></ul>',
      'auth.register.labelLogin': 'Логин',
      'auth.register.labelEmail': 'E-mail',
      'auth.register.labelPass': 'Құпия сөз (кемінде 4 таңба)',
      'auth.register.labelRole': 'Есептік жазба түрі',
      'auth.register.labelCompany': 'Ұйым атауы',
      'auth.register.phLoginSeeker': 'Мысалы: nur_serik',
      'auth.register.phLoginEmployer': 'Мысалы: too_dana_hr',
      'auth.register.phEmail': 'name@company.kz',
      'auth.register.phCompany': 'ЖШС «…», ЖК Иванов, клиника бренді',
      'auth.register.helpCompany': 'Кабинетте және бос орын карточкаларында қалай көрсетілетіні. Толтырмасаңыз — логин пайдаланылады.',
      'auth.register.optCompany': 'Тек жұмыс беруші / серіктес үшін',
      'auth.register.submit': 'Тіркелу',
      'auth.register.footer': 'Тіркелгенсіз бе?',
      'auth.register.footerLink': 'Кіру',
      'auth.register.roleSeeker': 'Жұмыс іздеуші (жеке тұлға)',
      'auth.register.roleEmployer': 'Жұмыс беруші / серіктес (заңды тұлға немесе ЖК)',

      'auth.err.shortUser': 'Логин кемінде 2 таңба болуы керек.',
      'auth.err.shortPass': 'Құпия сөз кемінде 4 таңба болуы керек.',
      'auth.err.badLogin': 'Логин немесе құпия сөз қате.',
      'auth.err.taken': 'Бұл логин қолжетімсіз. Басқасын көрсетіңіз.',
      'auth.ok.welcome': 'Қош келдіңіз, ',
      'auth.ok.register': 'Тіркелу сәтті аяқталды.',

      'dash.seeker.title': 'Жұмыс іздеушінің жеке кабинеті',
      'dash.seeker.lead': 'Сәлеметсіз бе, ',
      'dash.seeker.leadEnd': ' Төменде порталдағы белсенділігіңіздің қорытындысы көрсетілген.',
      'dash.seeker.s1': 'Өтінімдер',
      'dash.seeker.s2': 'Профиль қараулары',
      'dash.seeker.s3': 'Сақталған бос орындар',
      'dash.seeker.nextTitle': 'Келесі қадамдар',
      'dash.seeker.n1': 'Түйіндемеңізді толтырыңыз немесе жаңартыңыз — жұмыс берушілер сізді тезірек табады.',
      'dash.seeker.n2': 'Таңдаған сала мен қала бойынша жаңа бос орындар туралы хабарламаларды баптаңыз.',
      'dash.seeker.n3': 'Сәйкес ұсыныстарға өтінім жіберіп, «Менің өтінімдерім» бөлімінде мәртебені бақылаңыз.',
      'dash.seeker.hint': 'Сол жақтағы бөлімдер толық функционал қосылған сайын толық экрандарды ашады.',
      'dash.seeker.link': 'Бос орындар каталогына өту',
      'dash.seeker.nav1': 'Басты бет (дашборд)',
      'dash.seeker.nav2': 'Менің түйіндемелерім',
      'dash.seeker.nav3': 'Менің өтінімдерім',
      'dash.seeker.nav4': 'Сақталған бос орындар',
      'dash.seeker.nav5': 'Профиль баптаулары',
      'dash.seeker.nav6': 'Хабарламалар',
      'dash.seeker.docTitle': 'Жұмыс іздеуші кабинеті — Бос орындар порталы',

      'dash.employer.title': 'Жұмыс берушінің жеке кабинеті',
      'dash.employer.lead': 'Ұйым: ',
      'dash.employer.leadEnd': ' Орналастырылған бос орындар мен кандидаттардың өтінімдерінің қорытындысы.',
      'dash.employer.s1': 'Белсенді бос орындар',
      'dash.employer.s2': 'Жаңа өтінімдер',
      'dash.employer.s3': 'Апталық сұхбаттар',
      'dash.employer.nextTitle': 'ҚР жұмыс берушілері мен серіктестері үшін ұсыныстар',
      'dash.employer.n1': 'Баптауларда деректемелерді (БСН, заңды мекенжай) тексеріңіз — іздеушілердің сенімі үшін маңызды.',
      'dash.employer.n2': 'Бос орын сипаттамаларында жұмыс форматын, аудан немесе қашықтан жұмысты анық көрсетіңіз.',
      'dash.employer.n3': 'Өтінімдерге разумды мерзімде жауап беріңіз — бұл компанияның рейтингін арттырады.',
      'dash.employer.hint': 'Кабинет интерфейсі жұмыс іздеуші кабинетімен үйлесімді — екі тарап үшін ыңғайлы.',
      'dash.employer.link': 'Бос орындар каталогын ашу',
      'dash.employer.nav1': 'Басты бет (дашборд)',
      'dash.employer.nav2': 'Менің бос орындарым',
      'dash.employer.nav3': 'Бос орындарға өтінімдер',
      'dash.employer.nav4': 'Түйіндеме іздеу',
      'dash.employer.nav5': 'Компания баптаулары',
      'dash.employer.nav6': 'Хабарламалар',
      'dash.employer.docTitle': 'Жұмыс беруші кабинеті — Бос орындар порталы',
    },
  };

  function pack(lang) {
    return STR[lang] || STR.ru;
  }

  function JobPortalI18n() {}

  JobPortalI18n.getLang = function () {
    try {
      var v = localStorage.getItem(LS_KEY);
      return v === 'kk' ? 'kk' : 'ru';
    } catch (e) {
      return 'ru';
    }
  };

  JobPortalI18n.setLang = function (l) {
    if (l !== 'kk') l = 'ru';
    try {
      localStorage.setItem(LS_KEY, l);
    } catch (e) {}
    document.documentElement.setAttribute('lang', l === 'kk' ? 'kk' : 'ru');
    document.body.setAttribute('data-lang', l);
    JobPortalI18n.apply();
    document.dispatchEvent(
      new CustomEvent('jobportal:langchange', { detail: { lang: l } }),
    );
  };

  JobPortalI18n.t = function (key, lang) {
    var l = lang || JobPortalI18n.getLang();
    var table = pack(l);
    if (Object.prototype.hasOwnProperty.call(table, key)) return table[key];
    return pack('ru')[key] != null ? pack('ru')[key] : key;
  };

  JobPortalI18n.apply = function () {
    var lang = JobPortalI18n.getLang();
    document.documentElement.setAttribute('lang', lang === 'kk' ? 'kk' : 'ru');
    document.body.setAttribute('data-lang', lang);

    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      if (!key) return;
      el.textContent = JobPortalI18n.t(key, lang);
    });

    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-html');
      if (!key) return;
      el.innerHTML = JobPortalI18n.t(key, lang);
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-placeholder');
      if (!key) return;
      el.setAttribute('placeholder', JobPortalI18n.t(key, lang));
    });

    document.querySelectorAll('[data-i18n-title]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-title');
      if (!key) return;
      el.setAttribute('title', JobPortalI18n.t(key, lang));
    });

    document.querySelectorAll('[data-i18n-aria-label]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-aria-label');
      if (!key) return;
      el.setAttribute('aria-label', JobPortalI18n.t(key, lang));
    });

    var docTitleKey =
      document.body.getAttribute('data-i18n-doc-title') ||
      document.body.getAttribute('data-dashboard-doc');
    if (docTitleKey) {
      document.title = JobPortalI18n.t(docTitleKey, lang);
    }

    document.querySelectorAll('[data-lang-active]').forEach(function (btn) {
      var want = btn.getAttribute('data-lang-active');
      btn.classList.toggle('is-active', want === lang);
    });
  };

  JobPortalI18n.mountLangSwitch = function (container) {
    if (!container || container.getAttribute('data-i18n-mounted')) return;
    container.setAttribute('data-i18n-mounted', '1');
    container.innerHTML =
      '<div class="mock-lang-switch" role="group" data-i18n-aria-label="shell.langAria">' +
      '<button type="button" class="mock-lang-switch__btn" data-lang-set="ru" data-lang-active="ru">RU</button>' +
      '<button type="button" class="mock-lang-switch__btn" data-lang-set="kk" data-lang-active="kk">KZ</button>' +
      '</div>';
    container.querySelectorAll('[data-lang-set]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        JobPortalI18n.setLang(btn.getAttribute('data-lang-set'));
      });
    });
  };

  try {
    var early = localStorage.getItem(LS_KEY);
    if (early === 'kk') {
      document.documentElement.setAttribute('lang', 'kk');
    }
  } catch (e) {}

  global.JobPortalI18n = JobPortalI18n;
})(typeof window !== 'undefined' ? window : this);
