SELECT s.name AS subject, d.description AS deck, t.name AS topic, f.front
FROM flashcards f
JOIN topics t   ON f.topic_id = t.id
JOIN decks d    ON t.deck_id  = d.id
JOIN subjects s ON d.subject_id = s.id;