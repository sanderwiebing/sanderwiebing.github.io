---
layout: default
is_contact: true
---

## Contact

If you have a question, ideas or just want to get in touch, feel free to send me a message.

<ul class="contact-list">
  <li><span class="contact-icon">{% include icons/email.svg %}</span>{% include email.html %}</li>
  {% if site.social.github and site.social.github != "" %}<li><a href="{{ site.social.github }}"><span class="contact-icon">{% include icons/github.svg %}</span>GitHub</a></li>{% endif %}
  {% if site.social.scholar and site.social.scholar != "" %}<li><a href="{{ site.social.scholar }}"><span class="contact-icon">{% include icons/scholar.svg %}</span>Google Scholar</a></li>{% endif %}
  {% if site.social.linkedin and site.social.linkedin != "" %}<li><a href="{{ site.social.linkedin }}"><span class="contact-icon">{% include icons/linkedin.svg %}</span>LinkedIn</a></li>{% endif %}
</ul>
