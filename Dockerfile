FROM rasa/rasa:2.1.2-full

COPY . /app

RUN echo '#!/bin/bash' >> ./entrypoint.sh && \
    echo 'rasa run -p $PORT' >> ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
