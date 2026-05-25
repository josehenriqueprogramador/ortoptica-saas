FROM php:8.3-cli

RUN apt-get update && apt-get install -y \
    git curl libpng-dev libonig-dev libxml2-dev zip unzip libzip-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-install pdo_mysql mbstring zip exif pcntl bcmath gd
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www
EXPOSE 8000

CMD sh -c "if [ ! -f artisan ]; then composer create-project laravel/laravel . ; fi && composer install && php artisan key:generate --skip && php artisan serve --host=0.0.0.0 --port=8000"
