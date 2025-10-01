from app import db, create_app
from app.models.products import Product, Category

app = create_app()

with app.app_context():
    # Crear categorías si no existen
    cat_sneakers = Category.query.filter_by(name='Sneakers').first()
    if not cat_sneakers:
        cat_sneakers = Category(name='Sneakers', description='Zapatillas deportivas modernas')
        db.session.add(cat_sneakers)

    cat_running = Category.query.filter_by(name='Running').first()
    if not cat_running:
        cat_running = Category(name='Running', description='Zapatos para correr')
        db.session.add(cat_running)

    cat_casual = Category.query.filter_by(name='Casual').first()
    if not cat_casual:
        cat_casual = Category(name='Casual', description='Zapatos casuales para uso diario')
        db.session.add(cat_casual)

    db.session.commit()

    # Productos de ejemplo
    productos = [
        Product(
            name='Sneaker Air Max',
            description='Zapatilla deportiva con cámara de aire y diseño moderno.',
            price=89.99,
            stock=15,
            image='airmax.jpg',
            size='41',
            color='Blanco',
            category_id=cat_sneakers.id,
            promo='¡Envío gratis!',
            destacado=True
        ),
        Product(
            name='Runner Pro',
            description='Zapato ligero para correr largas distancias.',
            price=74.50,
            stock=20,
            image='runnerpro.jpg',
            size='42',
            color='Negro',
            category_id=cat_running.id,
            promo='10% de descuento',
            destacado=False
        ),
        Product(
            name='Casual Street',
            description='Zapato casual cómodo y versátil para el día a día.',
            price=59.90,
            stock=25,
            image='casualstreet.jpg',
            size='40',
            color='Azul',
            category_id=cat_casual.id,
            promo=None,
            destacado=False
        ),
        Product(
            name='Sneaker Classic',
            description='Zapatilla clásica con suela antideslizante.',
            price=65.00,
            stock=10,
            image='classic.jpg',
            size='43',
            color='Gris',
            category_id=cat_sneakers.id,
            promo=None,
            destacado=False
        ),
        Product(
            name='Urban Style',
            description='Zapato urbano con diseño moderno y materiales resistentes.',
            price=79.99,
            stock=18,
            image='urbanstyle.jpg',
            size='42',
            color='Negro',
            category_id=cat_casual.id,
            promo='2x1 en modelos seleccionados',
            destacado=True
        ),
        Product(
            name='Runner Flash',
            description='Zapatilla para running con máxima amortiguación.',
            price=92.00,
            stock=12,
            image='runnerflash.jpg',
            size='41',
            color='Rojo',
            category_id=cat_running.id,
            promo=None,
            destacado=False
        ),
        Product(
            name='Sneaker Neon',
            description='Zapatilla deportiva con detalles neón y suela flexible.',
            price=85.50,
            stock=14,
            image='neon.jpg',
            size='40',
            color='Verde',
            category_id=cat_sneakers.id,
            promo='¡Novedad!',
            destacado=True
        ),
        Product(
            name='Casual Brown',
            description='Zapato casual en cuero marrón, ideal para oficina.',
            price=70.00,
            stock=8,
            image='casualbrown.jpg',
            size='42',
            color='Marrón',
            category_id=cat_casual.id,
            promo=None,
            destacado=False
        ),
        Product(
            name='Runner Blue',
            description='Zapatilla para correr con malla transpirable.',
            price=78.00,
            stock=16,
            image='runnerblue.jpg',
            size='41',
            color='Azul',
            category_id=cat_running.id,
            promo='¡Oferta especial!',
            destacado=False
        ),
        Product(
            name='Sneaker Pink',
            description='Zapatilla deportiva color rosa, edición limitada.',
            price=88.00,
            stock=7,
            image='pink.jpg',
            size='39',
            color='Rosa',
            category_id=cat_sneakers.id,
            promo=None,
            destacado=True
        ),
    ]

    for prod in productos:
        exists = Product.query.filter_by(name=prod.name).first()
        if not exists:
            db.session.add(prod)

    db.session.commit()
    print('Productos de ejemplo agregados.')
