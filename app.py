from flask import Flask, g, session, request, abort, redirect, url_for, render_template
import sqlite3
from math import ceil
import mercadopago
from datetime import datetime
from config import SECRET_KEY, access_token

import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')

knowledge_base = {
    "Hola":
        "¡Hola! Bienvenido a nuestra aplicación de pedidos en farmacias. ¿En qué puedo ayudarte hoy?",
    "¿Cómo funciona la aplicación?":
        "Nuestra aplicación te permite realizar pedidos de productos farmacéuticos desde tu hogar. Puedes buscar productos, agregarlos al carrito y seleccionar la farmacia de tu elección para el retiro o entrega.",
    
    "¿Cuáles son las ventajas de usar esta aplicación en comparación con ir a la farmacia físicamente?":
        "Nuestra aplicación te ahorra tiempo al evitar desplazamientos. Puedes explorar productos, verificar la disponibilidad, comparar precios y recibir notificaciones sobre ofertas especiales.",
    
    "¿Qué tipos de productos puedo ordenar a través de la aplicación?":
        "Puedes pedir medicamentos recetados, medicamentos de venta libre, productos de cuidado personal, suplementos y más.",
    
    "¿Cuáles son las ofertas actuales disponibles en las farmacias?":
        "Actualmente, tenemos ofertas en vitaminas y suplementos, así como descuentos en productos para el cuidado de la piel.",
    
    "¿Puedo realizar un pedido y luego recogerlo en la farmacia más cercana?":
        "¡Claro! Puedes hacer un pedido y elegir la opción de recogida en la farmacia que te resulte más conveniente. Te notificaremos cuando esté listo.",
    
    "¿Cómo encuentro la farmacia más cercana a mi ubicación?":
        "La aplicación muestra las farmacias cercanas según tu ubicación. Puedes usar la búsqueda o permitir que acceda a tu ubicación.",
    
    "¿Cuáles son los horarios de atención de las farmacias?":
        "Los horarios varían. La mayoría está abierta de lunes a viernes de 8 AM a 8 PM, y los fines de semana de 9 AM a 6 PM.",
    
    "¿Puedo renovar mis recetas médicas a través de la aplicación?":
        "Actualmente, la renovación de recetas no está disponible en la aplicación. Contacta a tu médico para renovarlas.",
    
    "¿Cómo puedo realizar el pago de mi pedido?":
        "Aceptamos pagos en línea con tarjetas de crédito y débito. También puedes pagar en efectivo al recoger el pedido.",
    
    "¿Qué debo hacer si tengo problemas con mi pedido o necesito ayuda adicional?":
        "Comunícate con nuestro servicio al cliente al 123-456-7890 o escríbenos a farmago.shop@gmail.com",
    
    "¿Puedo obtener asesoramiento sobre medicamentos a través de la aplicación?":
        "Nuestra aplicación ofrece información general sobre medicamentos, pero siempre es recomendable consultar a un profesional de la salud para obtener asesoramiento médico específico.",
    
    "¿Cómo puedo buscar un producto en la aplicación?":
        "Puedes usar la función de búsqueda en la parte superior de la pantalla para encontrar productos por nombre, categoría o palabra clave.",
    
    "¿Las farmacias aceptan seguros médicos para los pagos?":
        "Sí, muchas de nuestras farmacias asociadas aceptan seguros médicos. Puedes verificar la opción de pago al realizar el pedido.",
    
    "¿Ofrecen entregas a domicilio?":
        "Sí, ofrecemos entregas a domicilio en áreas seleccionadas. Puedes seleccionar la opción de entrega al realizar tu pedido.",
    
    "¿Cuánto tiempo tardará en llegar mi pedido a mi domicilio?":
        "El tiempo de entrega puede variar según tu ubicación y la disponibilidad de productos. Te proporcionaremos una estimación al confirmar tu pedido.",
    
    "¿Puedo realizar cambios en mi pedido después de haberlo realizado?":
        "Una vez que hayas realizado el pedido, es posible que no puedas hacer cambios. Te recomendamos revisar cuidadosamente antes de confirmar.",
    
    "¿Cómo puedo rastrear el estado de mi pedido?":
        "Puedes rastrear el estado de tu pedido a través de la aplicación. Te enviaremos notificaciones sobre su progreso.",
    
    "¿Cuáles son los métodos de entrega disponibles?":
        "Ofrecemos opciones de recogida en la farmacia y entregas a domicilio, según tu preferencia y disponibilidad.",
    
    "¿Qué debo hacer si olvidé mi contraseña de la cuenta?":
        "Puedes usar la opción 'Recuperar contraseña' en la pantalla de inicio de sesión para restablecerla.",
    
    "¿La aplicación está disponible para dispositivos iOS y Android?":
        "Sí, nuestra aplicación está disponible tanto en la App Store de iOS como en Google Play Store para dispositivos Android.",
    
    "¿Puedo cancelar mi pedido después de haberlo confirmado?":
        "Dependiendo del estado de tu pedido y las políticas de la farmacia, es posible que puedas cancelarlo. Te recomendamos contactar a la farmacia lo antes posible para obtener ayuda.",
    
    "¿Cómo puedo verificar la disponibilidad de un producto en una farmacia específica?":
        "Puedes buscar el producto que deseas y seleccionar la farmacia de tu elección para ver si está disponible.",
    
    "¿Se requiere receta médica para comprar medicamentos recetados?":
        "Sí, generalmente se requiere una receta médica válida para comprar medicamentos recetados. Asegúrate de proporcionar la receta al realizar el pedido.",
    
    "¿Cómo puedo agregar productos a mi lista de favoritos?":
        "Puedes marcar productos como favoritos haciendo clic en el botón de 'Agregar a favoritos' en la página del producto.",
    
    "¿Ofrecen descuentos especiales para clientes frecuentes?":
        "Sí, tenemos un programa de recompensas para clientes frecuentes que ofrece descuentos y ofertas exclusivas.",
    
    "¿Puedo hacer devoluciones o cambios en los productos que he comprado?":
        "Las políticas de devolución y cambio pueden variar según la farmacia. Te recomendamos comunicarte con la farmacia para obtener información específica.",
    
    "¿Qué métodos de pago aceptan para las compras?":
        "Aceptamos pagos en línea con tarjetas de crédito y débito de las principales marcas.",
    
    "¿Puedo programar la entrega de mi pedido para un horario específico?":
        "En la mayoría de los casos, puedes elegir una franja horaria para la entrega de tu pedido. Selecciona la opción adecuada durante el proceso de pedido.",
    
    "¿Cómo puedo actualizar la información de mi cuenta, como la dirección de entrega?":
        "Puedes actualizar la información de tu cuenta en la sección 'Configuración' de la aplicación.",
    
    "¿Qué debo hacer si no recibí la notificación de mi pedido listo para recoger?":
        "Si no recibiste una notificación, te recomendamos comunicarte con la farmacia para confirmar el estado de tu pedido.",
    
    "¿Ofrecen productos orgánicos y naturales en la aplicación?":
        "Sí, ofrecemos una variedad de productos orgánicos y naturales en nuestra plataforma.",
    
    "¿Puedo recibir ayuda en vivo a través del chat de la aplicación?":
        "Sí, ofrecemos asistencia en vivo a través del chat de la aplicación durante las horas de atención al cliente.",
    
    "¿Cómo puedo realizar un seguimiento de mis gastos en la aplicación?":
        "Puedes consultar el historial de pedidos en tu cuenta para realizar un seguimiento de tus gastos anteriores.",
    
    "¿Las farmacias ofrecen servicios de consulta médica a través de la aplicación?":
        "Algunas farmacias pueden ofrecer servicios de consulta médica en línea. Verifica la disponibilidad en la sección de servicios de la farmacia.",
    
    "¿Puedo obtener reembolso si mi pedido llega dañado o incompleto?":
        "Sí, si tu pedido llega dañado o incompleto, comunícate con la farmacia para gestionar un reembolso o reemplazo.",
    
    "¿Cuánto tiempo se guardan mis datos personales en la aplicación?":
        "Respetamos tu privacidad. Puedes consultar nuestra política de privacidad para obtener información detallada sobre la retención de datos.",
    
    "¿Puedo obtener información sobre interacciones entre medicamentos a través de la aplicación?":
        "Nuestra aplicación ofrece información básica sobre interacciones entre medicamentos, pero siempre es aconsejable consultar a un profesional de la salud para obtener asesoramiento específico.",
    
    "¿Tienen un programa de lealtad para acumular puntos por compras?":
        "Sí, tenemos un programa de lealtad que te permite acumular puntos por tus compras y canjearlos por descuentos y recompensas.",
    
    "¿La aplicación ofrece recordatorios para tomar medicamentos?":
        "Sí, puedes configurar recordatorios en la aplicación para recibir notificaciones y asegurarte de tomar tus medicamentos a tiempo.",
    
    "¿La aplicación ofrece información sobre alergias o restricciones alimentarias?":
        "Sí, proporcionamos información sobre alergias y restricciones alimentarias para algunos productos. Si tienes preocupaciones específicas, te recomendamos verificar los detalles del producto o contactar a la farmacia.",
    
    "¿Qué debo hacer si tengo problemas con el proceso de pago?":
        "Si experimentas problemas con el proceso de pago, verifica que los detalles de la tarjeta sean correctos y asegúrate de tener suficientes fondos. Si el problema persiste, comunícate con nuestro equipo de soporte.",
    
    "¿Puedo comprar productos de cuidado infantil a través de la aplicación?":
        "Sí, ofrecemos una variedad de productos de cuidado infantil, como pañales, fórmula para bebés y productos de higiene.",
    
    "¿Cuánto tiempo toma procesar mi pedido antes de la entrega o recogida?":
        "El tiempo de procesamiento puede variar según la farmacia y la ubicación. Por lo general, intentamos procesar los pedidos lo más rápido posible para que estén listos en un plazo razonable.",
    
    "¿Puedo agregar varios destinos de entrega en un solo pedido?":
        "Actualmente, la función de agregar varios destinos de entrega en un solo pedido no está disponible. Debes hacer pedidos separados para diferentes direcciones de entrega.",
    
    "¿La aplicación ofrece opciones de idioma además del español?":
        "Por ahora, la aplicación está disponible solo en español. Estamos trabajando para agregar más opciones de idioma en futuras actualizaciones.",
    
    "¿Puedo ver las reseñas y calificaciones de los productos en la aplicación?":
        "Sí, puedes ver las reseñas y calificaciones de otros usuarios para algunos productos. Esto puede ayudarte a tomar decisiones informadas al realizar un pedido.",
    
    "¿Cómo puedo buscar productos específicos de una marca en particular?":
        "Puedes buscar productos de una marca específica utilizando la función de búsqueda y agregando el nombre de la marca como palabra clave.",
    
    "¿Puedo hacer cambios en mi cuenta, como cambiar mi dirección de correo electrónico?":
        "Sí, puedes realizar cambios en tu cuenta, incluida la dirección de correo electrónico, en la sección de configuración de la aplicación.",
    
    "¿Qué información necesito proporcionar al realizar un pedido de medicamentos recetados?":
        "Debes proporcionar la información de la receta médica, incluido el nombre del medicamento, la dosis, las instrucciones y el médico que la recetó.",
    
    "¿La aplicación ofrece opciones de entrega exprés para pedidos urgentes?":
        "Sí, ofrecemos opciones de entrega exprés para pedidos urgentes. Puedes seleccionar esta opción al finalizar el pedido.",
    
    "¿Cómo puedo estar al tanto de las últimas ofertas y promociones?":
        "Puedes suscribirte a nuestras notificaciones y boletines para recibir información sobre las últimas ofertas y promociones en la aplicación.",
    
    "¿Puedo programar una entrega para una fecha futura específica?":
        "Sí, puedes programar una entrega para una fecha futura específica durante el proceso de pedido.",
    
    "¿La aplicación permite hacer seguimiento de mi historial de compras anteriores?":
        "Sí, puedes acceder a tu historial de compras anteriores en la sección de 'Mis pedidos' de la aplicación.",
    
    "¿Ofrecen servicios de asesoría en salud a través de la aplicación?":
        "Actualmente, no ofrecemos servicios de asesoría en salud a través de la aplicación. Te recomendamos consultar a un profesional médico para obtener asesoramiento personalizado.",
    
    "¿Puedo pedir productos en grandes cantidades a través de la aplicación?":
        "Sí, puedes realizar pedidos de grandes cantidades de productos. Ten en cuenta que algunas restricciones podrían aplicar según la disponibilidad.",
    
    "¿La aplicación proporciona información nutricional para los productos?":
        "Proporcionamos información nutricional para algunos productos alimenticios. Debes verificar la página del producto para obtener detalles específicos.",
    
    "¿Puedo solicitar una factura después de realizar un pedido?":
        "Sí, puedes solicitar una factura después de realizar un pedido. Comunícate con la farmacia para obtener la factura correspondiente.",
    
    "¿Cómo puedo acceder a mis cupones y códigos de descuento en la aplicación?":
        "Puedes acceder a tus cupones y códigos de descuento en la sección de 'Cupones' o 'Ofertas' de la aplicación.",
    
    "¿Qué medidas de seguridad tienen en su plataforma para proteger mis datos personales?":
        "Nos tomamos en serio la seguridad de tus datos. Implementamos medidas de seguridad robustas para proteger tu información personal y financiera.",
    
    "¿Puedo realizar pedidos de productos fuera de mi país de residencia?":
        "Actualmente, solo aceptamos pedidos para entrega en áreas específicas dentro de tu país de residencia.",
    
    "¿Cómo puedo proporcionar comentarios o sugerencias sobre la aplicación?":
        "Valoramos tus comentarios. Puedes enviar tus sugerencias y comentarios a través de la sección de 'Contacto' en la aplicación.",
    
    "No puedo encontrar lo que necesito. ¿Puedes ayudarme?":
        "Por supuesto. Por favor, dime qué producto estás buscando o qué necesitas, y estaré encantado de ayudarte a encontrarlo.",
    
    "¿Qué marcas de productos ofrecen en la aplicación?":
        "Ofrecemos una amplia variedad de marcas reconocidas en la industria farmacéutica y de cuidado personal, como Bayer, Johnson & Johnson, y más.",
    
    "Necesito algo para el dolor de cabeza. ¿Qué me recomiendas?":
        "Para el dolor de cabeza, te recomendaría consultar nuestra sección de analgésicos, donde encontrarás opciones como acetaminofén o ibuprofeno.",
    
    "¿Hay algo nuevo o popular en la aplicación que debería ver?":
        "Sí, actualmente tenemos una promoción en productos para el cuidado de la piel. ¡Te recomiendo echar un vistazo a nuestras ofertas destacadas!",
    
    "Quiero mejorar mi sistema inmunológico. ¿Qué productos tienen para eso?":
        "Para mejorar tu sistema inmunológico, te sugiero explorar nuestra sección de vitaminas y suplementos, donde encontrarás opciones como la vitamina C y el zinc.",
    
    "¿Qué debo hacer si mi pedido llega tarde o hay un problema con la entrega?":
        "Si tu pedido se retrasa o experimentas problemas con la entrega, te recomiendo comunicarte con nuestro equipo de atención al cliente para que podamos resolverlo.",
    
    "¿Tienen productos naturales para el alivio de resfriados y gripes?":
        "Sí, ofrecemos una selección de productos naturales como tés de hierbas y suplementos que pueden ayudar en el alivio de resfriados y gripes.",
    
    "Quiero algo para el cuidado de mis pies. ¿Qué opciones tienen?":
        "Para el cuidado de tus pies, te invito a explorar nuestra sección de productos para el cuidado personal, donde encontrarás cremas hidratantes y productos para el cuidado de los pies.",
    
    "Estoy buscando algo para aliviar la congestión nasal. ¿Puedes sugerirme algo?":
        "Para aliviar la congestión nasal, te recomiendo revisar nuestra categoría de descongestionantes nasales, donde encontrarás opciones efectivas.",
    
    "¿Cuál es la diferencia entre los productos genéricos y de marca?":
        "Los productos genéricos generalmente contienen los mismos ingredientes activos que los de marca, pero pueden ser más económicos. Te invito a comparar las opciones disponibles.",
    
    "¿Qué me recomiendas para el cuidado del cabello dañado?":
        "Para el cuidado del cabello dañado, te sugeriría examinar nuestra selección de productos para el cuidado del cabello, incluidos acondicionadores y tratamientos reparadores.",
    
    "No estoy seguro de qué producto necesito. ¿Puedes guiarme en la dirección correcta?":
        "Por supuesto, ¿hay algo en particular en lo que estés interesado o alguna preocupación específica que pueda ayudarte a abordar?",
    
    "¿Puedo usar mi seguro médico para pagar los productos recetados?":
        "Sí, en algunas farmacias aceptamos seguros médicos para el pago de productos recetados. Asegúrate de verificar las opciones de pago al finalizar tu pedido.",
    
    "¿Tienen productos para el cuidado de la piel sensible?":
        "Sí, ofrecemos una selección de productos específicamente diseñados para el cuidado de la piel sensible. Te recomendaría explorar nuestra sección de cuidado facial.",
    
    "¿Hay algún producto en oferta para el alivio del estrés o la ansiedad?":
        "Actualmente, tenemos ofertas en suplementos naturales que pueden ayudar en el alivio del estrés y la ansiedad. Te sugiero explorar nuestra sección de bienestar.",
    
    "Quiero algo para mantener mi energía durante el día. ¿Qué me sugieres?":
        "Para mantener la energía durante el día, puedes explorar nuestra selección de suplementos energéticos y vitaminas B.",
    
    "Estoy buscando productos para bebés. ¿Qué tienen disponible?":
        "Tenemos una variedad de productos para bebés, como pañales, fórmula para bebés, productos de higiene y más. Te invito a explorar nuestra sección de cuidado infantil.",
    
    "¿Cómo puedo verificar la disponibilidad de un producto en mi farmacia local?":
        "Puedes utilizar la función de búsqueda y seleccionar tu farmacia local para ver la disponibilidad de productos en esa ubicación.",
    
    "Quiero algo para mejorar mi sueño. ¿Qué opciones tienen?":
        "Para mejorar el sueño, te recomiendo explorar nuestra selección de suplementos naturales para el sueño, como la melatonina.",
    
    "¿Puedo obtener ayuda para encontrar alternativas genéricas a los medicamentos recetados?":
        "Por supuesto, puedo ayudarte a buscar alternativas genéricas a los medicamentos recetados. Por favor, proporciona el nombre del medicamento para que pueda asistirte mejor.",
    
    "Necesito algo para el dolor muscular. ¿Tienen productos para eso?":
        "Para el dolor muscular, te sugiero revisar nuestra selección de analgésicos tópicos y cremas para el alivio del dolor.",
    
    "¿Puedo recibir información sobre cómo cuidar la piel seca?":
        "Claro, puedo proporcionarte consejos y recomendaciones sobre cómo cuidar la piel seca. ¿Deseas sugerencias para productos específicos?",
    
    "¿Cuál es el producto más popular en la categoría de cuidado facial?":
        "Uno de nuestros productos más populares en la categoría de cuidado facial es la crema hidratante de ácido hialurónico. ¡Te recomiendo probarla!",
    
    "No sé qué producto elegir. ¿Puedes decirme cuáles son los más vendidos?":
        "Por supuesto, algunos de nuestros productos más vendidos incluyen vitaminas, analgésicos y productos de cuidado facial. ¿Hay alguna categoría en particular que te interese?",
    
    "¿Cómo usar esta app?":
        "Puedes comprar medicamentos y productos a través de la aplicación. Busca los productos que necesitas, agrégalos al carrito, realiza el pago y elige la opción de recoger en la farmacia que prefieras. Te notificaremos cuando tu pedido esté listo para recoger.",
    
    "¿Ventajas de app vs. farmacia?":
        "La aplicación te permite ahorrar tiempo al evitar desplazamientos a la farmacia. Puedes explorar una amplia gama de productos desde la comodidad de tu hogar, ver ofertas especiales y comparar precios antes de hacer tu compra.",
    
    "¿Productos en app?":
        "En la aplicación, encontrarás una variedad de productos que incluyen medicamentos recetados y de venta libre, productos de cuidado personal como cremas, lociones y champús, vitaminas, suplementos y más.",
    
    "¿Ofertas actuales?":
        "En este momento, tenemos descuentos en una variedad de productos, incluyendo vitaminas y productos para el cuidado de la piel. Puedes explorar nuestras ofertas en la sección correspondiente de la aplicación.",
    
    "¿Ordenar y recoger?":
        "El proceso es sencillo. Después de agregar los productos a tu carrito y realizar el pago, selecciona la farmacia donde deseas recoger tus productos. Te notificaremos cuando tu pedido esté listo para ser retirado en la ubicación que elijas.",
    
    "¿Farmacia cercana?":
        "Puedes encontrar farmacias cercanas utilizando la función de búsqueda en la aplicación. También puedes permitir que la aplicación acceda a tu ubicación para mostrar las farmacias más cercanas según tu posición actual.",
    
    "¿Horarios de farmacia?":
        "Los horarios de las farmacias pueden variar, pero en general, muchas de nuestras farmacias asociadas están abiertas de lunes a viernes de 8 AM a 8 PM, y los fines de semana de 9 AM a 6 PM. Te recomendamos verificar los horarios específicos de la farmacia en la que planeas recoger tus productos.",
    
    "¿Renovar recetas app?":
        "Actualmente, no es posible renovar recetas médicas a través de la aplicación. Debes ponerte en contacto con tu médico para solicitar la renovación de tus recetas.",
    
    "¿Formas de pago?":
        "Aceptamos pagos en línea con tarjetas de crédito y débito de las principales marcas. También puedes optar por pagar en efectivo al momento de recoger tus productos en la farmacia.",
    
    "¿Problemas con pedido?":
        "Si tienes algún problema con tu pedido o necesitas asistencia adicional, puedes comunicarte con nuestro servicio al cliente. Simplemente llama al número de servicio al cliente que aparece en la aplicación y con gusto te ayudaremos a resolver cualquier problema que puedas tener.",
    
    "¿Cómo comprar aquí?":
        "Para realizar una compra en la aplicación, primero busca los productos que necesitas utilizando la función de búsqueda. Luego, agrega los productos al carrito de compras, sigue las indicaciones para completar el pago y elige la farmacia donde deseas recoger tus productos.",
    
    "¿Para qué es app?":
        "La aplicación está diseñada para facilitar tus compras de medicamentos y productos de cuidado personal. Puedes buscar productos, agregarlos al carrito, realizar pagos y elegir dónde recoger tus productos, todo desde tu dispositivo móvil.",
    
    "¿Nombres marcas aquí?":
        "Ofrecemos una amplia gama de productos de marcas conocidas en la industria farmacéutica y de cuidado personal. Puedes encontrar marcas como Bayer, Johnson & Johnson, y muchas otras en la aplicación.",
    
    "¿Hay promociones hoy?":
        "Sí, en este momento tenemos promociones y descuentos en una variedad de productos. Puedes explorar nuestras ofertas actuales en la sección de promociones dentro de la aplicación.",
    
    "¿Hacer pedido, luego qué?":
        "Después de hacer tu pedido y completar el pago, podrás elegir la farmacia donde deseas recoger tus productos. Una vez que tu pedido esté listo para ser retirado, te enviaremos una notificación para que sepas que puedes pasar a recogerlo.",
    
    "¿Cómo saber farmacia cerca?":
        "Utiliza la función de búsqueda en la aplicación y busca 'farmacias cercanas'. También puedes permitir que la aplicación acceda a tu ubicación para mostrarte las farmacias que están más cerca de ti.",
    
    "¿Horario de farmacias?":
        "Las horas de operación de las farmacias pueden variar según la ubicación. En general, muchas de nuestras farmacias asociadas están abiertas de lunes a viernes de 8 AM a 8 PM, y los fines de semana de 9 AM a 6 PM. Te recomendamos verificar los horarios específicos de la farmacia en la que planeas recoger tus productos.",
    
    "¿Renovar recetas aquí?":
        "No, actualmente no puedes renovar recetas médicas a través de la aplicación. Debes comunicarte con tu médico para solicitar la renovación de tus recetas.",
    
    "¿Formas de pagar compras?":
        "Aceptamos varias formas de pago, incluyendo tarjetas de crédito y débito de las principales marcas. También puedes optar por pagar en efectivo cuando recojas tus productos en la farmacia.",
    
    "¿Problemas con pedido, solución?":
        "Si enfrentas algún problema con tu pedido, te recomendamos llamar a nuestro servicio al cliente. Nuestro equipo estará disponible para ayudarte a resolver cualquier problema que puedas tener y encontrar una solución adecuada.",
    
    "¿Cómo buscar producto?":
        "Para buscar un producto específico, utiliza la función de búsqueda en la aplicación. Escribe el nombre del producto o una palabra clave relacionada y verás los resultados correspondientes.",
    
    "¿Productos para bebés?":
        "Tenemos una variedad de productos para bebés disponibles en la aplicación. Puedes encontrar pañales, productos de cuidado infantil, fórmula para bebés y más en nuestra selección.",
    
    "¿Medicamentos sin receta?":
        "Sí, puedes comprar medicamentos de venta libre sin necesidad de receta médica a través de la aplicación. Estos productos están disponibles para su compra directa.",
    
    "¿Consultar salud app?":
        "La aplicación no reemplaza la consulta médica. Si tienes preocupaciones sobre tu salud, es importante consultar a un médico en persona para obtener un diagnóstico y recomendaciones adecuadas.",
    
    "¿Cómo recibir mi pedido?":
        "Después de realizar tu pedido y recibir la notificación de que está listo, puedes dirigirte a la farmacia que elegiste para recoger tus productos. Asegúrate de llevar contigo una identificación válida al momento de recoger tu pedido."
}   

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [token for token in tokens if token not in stopwords.words('english') and token not in string.punctuation]
    return tokens

def get_synonyms(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
    return synonyms

def find_best_match(question, knowledge_base):
    question_words = preprocess_text(question)
    best_match = None
    max_similarity = 0
    for q, a in knowledge_base.items():
        answer_words = preprocess_text(q)
        similarity = len(set(question_words).intersection(answer_words))
        synonyms = get_synonyms(q)
        similarity += len(set(question_words).intersection(synonyms))
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = a
    return best_match

chat_history = []

DATABASE = 'FarmaGo.db'
app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_tables():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                apellido TEXT,
                direccion TEXT,
                numero_telefono TEXT,
                provincia TEXT,
                localidad TEXT,
                correo_electronico TEXT UNIQUE,
                nombre_usuario TEXT UNIQUE,
                contraseña TEXT,
                role TEXT,
                logo_url TEXT
            );
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                imagen TEXT,
                descripcion TEXT,
                cantidad INTEGER,
                precio_unitario REAL,
                id_categoria INTEGER,
                id_farmacia INTEGER, 
                FOREIGN KEY(id_categoria) REFERENCES categorias(id),
                FOREIGN KEY(id_farmacia) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT
            );
            CREATE TABLE IF NOT EXISTS farmacia_productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                id_producto INTEGER,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            );
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_farmacia INTEGER,
                id_producto INTEGER,
                cantidad_disponible INTEGER,
                FOREIGN KEY(id_farmacia) REFERENCES usuarios(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            );
            CREATE TABLE IF NOT EXISTS carritos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                fecha TEXT,
                estado TEXT,
                total REAL,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS detalles_carrito (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_carrito INTEGER,
                id_producto INTEGER,
                cantidad INTEGER,
                precio_unitario REAL,
                FOREIGN KEY(id_carrito) REFERENCES carritos(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            );
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_vendedor INTEGER,
                id_comprador INTEGER,
                fecha TEXT,
                total REAL,
                FOREIGN KEY(id_vendedor) REFERENCES usuarios(id),
                FOREIGN KEY(id_comprador) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS detalles_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venta INTEGER,
                id_producto INTEGER,
                cantidad INTEGER,
                precio_unitario REAL,
                FOREIGN KEY(id_venta) REFERENCES ventas(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            );
        ''')
        db.commit()

def get_user_id(correo_electronico):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE correo_electronico = ?', (correo_electronico,))
        result = cursor.fetchone()
        return result[0] if result else None

def get_farmacia_info(id_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, contraseña, logo_url FROM usuarios WHERE id = ?', (id_usuario,))
        result = cursor.fetchone()
        return result if result else None

def get_user_info(id_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, contraseña, logo_url FROM usuarios WHERE id = ?', (id_usuario,))
        result = cursor.fetchone()
        return result if result else None

def get_user_role(nombre_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT role FROM usuarios WHERE nombre_usuario = ?', (nombre_usuario,))
        result = cursor.fetchone()
        return result[0] if result else None

def authenticate_user(correo_electronico, contraseña):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, role FROM usuarios WHERE correo_electronico = ? AND contraseña = ?', (correo_electronico, contraseña))
        result = cursor.fetchone()
        if result:
            return result[0], result[1]
        return None, None

def register_user(nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico,logo_url=None):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE nombre_usuario = ?', (nombre_usuario,))
        existing_username = cursor.fetchone()
        if existing_username:
            return "El nombre de usuario ya está en uso. Por favor, elige otro."
        cursor.execute('SELECT id FROM usuarios WHERE correo_electronico = ?', (correo_electronico,))
        existing_user = cursor.fetchone()
        if existing_user:
            return "El correo electrónico ya está en uso. Por favor, elige otro."
        if role == 'farmacia':
            cursor.execute('INSERT INTO usuarios (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, logo_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, logo_url))
            farmacia_id = cursor.lastrowid
            db.commit()
            cursor.execute('SELECT id FROM productos')
            productos = cursor.fetchall()
            for producto in productos:
                cursor.execute('INSERT INTO inventario (id_farmacia, id_producto, cantidad_disponible) VALUES (?, ?, ?)', (farmacia_id, producto[0], 0))
            db.commit()
        else:
            cursor.execute('INSERT INTO usuarios (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, logo_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, logo_url))
        db.commit()

def crear_enlace_de_pago(producto, precio, moneda='ARS', cantidad=1, descripcion=''):
    mp = mercadopago.SDK(access_token)
    preference_data = {
        "items": [
            {
                "title": producto,
                "quantity": cantidad,
                "currency_id": moneda,
                "unit_price": precio,
            }
        ],
        "back_urls": {
            "success": "192.168.0.106:5000/pago_exitoso",
            "failure": "192.168.0.106:5000/pago_fallido",
            "pending": "192.168.0.106:5000/pago_pendiente",
        },
        "auto_return": "approved",
    }
    preference = mp.preference().create(preference_data)
    return preference['response']['init_point']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/help')
def help():
    return render_template('chat.html', chat_history=chat_history)

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    chat_history.append(('user', user_input))
    if user_input.lower() == 'salir' or user_input.lower() == 'adios':
        response = "¡Hasta luego!"
        chat_history.clear()
    else:
        response = find_best_match(user_input, knowledge_base) or "Lo siento, no entendí la pregunta."
    chat_history.append(('bot', response))
    return render_template('chat.html', chat_history=chat_history)

@app.route('/perfil')
def perfil():
    user_role = session.get('user_role')
    if user_role == 'farmacia' or user_role == 'cliente':
        return render_template('perfil.html')
    else:
        abort(403)

@app.route('/farmacia/inventario', methods=['GET', 'POST'])
def farmacia_inventario():
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        if request.method == 'POST':
            inventario = request.form.getlist('inventario')
            farmacia_id = session.get('user_id')
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('DELETE FROM inventario WHERE id_farmacia = ?', (farmacia_id,))
                for id_producto, cantidad in enumerate(inventario, start=1):
                    if cantidad.isdigit() and int(cantidad) >= 0:
                        cursor.execute('INSERT INTO inventario (id_farmacia, id_producto, cantidad_disponible) VALUES (?, ?, ?)', (farmacia_id, id_producto, cantidad))
                db.commit()
        else:
            farmacia_id = session.get('user_id')
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('SELECT p.id, p.nombre, COALESCE(i.cantidad_disponible, 0) as cantidad_disponible, p.cantidad, p.precio_unitario FROM productos p LEFT JOIN inventario i ON p.id = i.id_producto AND i.id_farmacia = ? WHERE p.id_farmacia = ?', (farmacia_id, farmacia_id))
                inventario = cursor.fetchall()
        return render_template('farmacia_inventario.html', inventario=inventario)
    else:
        abort(403)

@app.route('/productos', methods=['GET'])
def listar_productos():
    user_role = session.get('user_role')
    if user_role == 'farmacia' or user_role == 'cliente':
        pagina = request.args.get('pagina', default=1, type=int)
        productos_por_pagina = 9
        categoria_id = request.args.get('categoria_id', default=None, type=int)
        search_query = request.args.get('search_query')
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT id, nombre FROM categorias')
            categorias = cursor.fetchall()
            if categoria_id is not None:
                cursor.execute('SELECT COUNT(*) FROM productos WHERE id_categoria = ?', (categoria_id,))
                total_productos = cursor.fetchone()[0]
                total_paginas = ceil(total_productos / productos_por_pagina)
                if pagina < 1:
                    pagina = 1
                elif pagina > total_paginas:
                    pagina = total_paginas
                inicio = (pagina - 1) * productos_por_pagina
                cursor.execute('SELECT * FROM productos WHERE id_categoria = ? LIMIT ? OFFSET ?', (categoria_id, productos_por_pagina, inicio))
                productos = cursor.fetchall()
            elif search_query:
                with app.app_context():
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute('SELECT COUNT(*) FROM productos WHERE nombre LIKE ?', ('%' + search_query + '%',))
                    total_productos = cursor.fetchone()[0]
                    total_paginas = ceil(total_productos / productos_por_pagina)
                    if pagina < 1:
                        pagina = 1
                    elif pagina > total_paginas:
                        pagina = total_paginas
                    inicio = (pagina - 1) * productos_por_pagina
                    cursor.execute('SELECT * FROM productos WHERE nombre LIKE ? LIMIT ? OFFSET ?', ('%' + search_query + '%', productos_por_pagina, inicio))
                    productos = cursor.fetchall()
                return render_template('listar_productos.html', productos=productos, pagina=pagina, total_paginas=total_paginas, user_role=user_role, search_query=search_query)
            else:
                cursor.execute('SELECT COUNT(*) FROM productos')
                total_productos = cursor.fetchone()[0]
                total_paginas = ceil(total_productos / productos_por_pagina)
                if pagina < 1:
                    pagina = 1
                elif pagina > total_paginas:
                    pagina = total_paginas
                inicio = (pagina - 1) * productos_por_pagina
                cursor.execute('SELECT * FROM productos LIMIT ? OFFSET ?', (productos_por_pagina, inicio))
                productos = cursor.fetchall()
        return render_template('listar_productos.html', productos=productos, pagina=pagina, total_paginas=total_paginas, user_role=user_role, categorias=categorias, categoria_id=categoria_id)
    else:
        abort(403)

@app.route('/productos/<int:id_producto>', methods=['GET'])
def ver_detalle_producto(id_producto):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM productos WHERE id=?', (id_producto,))
        producto = cursor.fetchone()
        farmacia_info = get_farmacia_info(producto[7])  
        id_farmacia = producto[7]
        cursor.execute('SELECT nombre FROM categorias WHERE id=?', (producto[6],))
        categoria_nombre = cursor.fetchone()[0]
    if producto and farmacia_info:
        return render_template('detalle_producto.html', producto=producto, farmacia_info=farmacia_info, id_farmacia=id_farmacia, categoria_nombre=categoria_nombre)
    else:
        abort(404)

@app.route('/productos/categoria/<int:id_categoria>', methods=['GET'])
def productos_por_categoria(id_categoria):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM productos WHERE id_categoria = ?', (id_categoria,))
        productos = cursor.fetchall()
        cursor.execute('SELECT nombre FROM categorias WHERE id = ?', (id_categoria,))
        categoria_nombre = cursor.fetchone()[0]
    return render_template('productos_por_categoria.html', productos=productos, categoria_nombre=categoria_nombre)

@app.route('/todas_farmacias', methods=['GET', 'POST'])
def todas_farmacias():
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            if search_query:
                cursor.execute('SELECT * FROM usuarios WHERE role="farmacia" AND nombre LIKE ?', ('%' + search_query + '%',))
            else:
                cursor.execute('SELECT * FROM usuarios WHERE role="farmacia"')
            farmacias = cursor.fetchall()
    else:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE role="farmacia"')
            farmacias = cursor.fetchall()
    return render_template('todas_farmacias.html', farmacias=farmacias)

@app.route('/productos/farmacia/<int:id_usuario>', methods=['GET'])
def productos_por_farmacia(id_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM productos WHERE id_farmacia=?', (id_usuario,))
        productos = cursor.fetchall()
        farmacia_info = get_farmacia_info(id_usuario)
    return render_template('productos_farmacia.html', productos=productos, farmacia_info=farmacia_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo_electronico = request.form.get('correo_electronico')
        password = request.form.get('password')
        user_id, user_role = authenticate_user(correo_electronico, password)
        if user_id and user_role:
            session['user_id'] = user_id
            session['user_role'] = user_role
            return redirect(url_for('dashboard'))
        else:
            error="Credenciales inválidas. Por favor, inténtalo nuevamente."
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

@app.route('/register/cliente', methods=['GET', 'POST'])
def register_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        direccion = request.form['direccion']
        numero_telefono = request.form['numero_telefono']
        provincia = request.form['provincia']
        localidad = request.form['localidad']
        correo_electronico = request.form['correo_electronico']
        nombre_usuario = request.form['nombre_usuario']
        contraseña = request.form['contraseña']
        role = 'cliente'
        logo_url = request.form.get('logo_url')
        error_message = register_user(nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, logo_url=logo_url)
        if error_message:
            return render_template('register.html', error=error_message)
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/register/farmacia', methods=['GET', 'POST'])
def register_farmacia():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        direccion = request.form['direccion']
        numero_telefono = request.form['numero_telefono']
        provincia = request.form['provincia']
        localidad = request.form['localidad']
        correo_electronico = request.form['correo_electronico']
        nombre_usuario = request.form['nombre_usuario']
        contraseña = request.form['contraseña']
        role = 'farmacia'
        logo_url = request.form.get('logo_url')
        error_message = register_user(nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico,logo_url=logo_url)
        if error_message:
            return render_template('register.html', error=error_message)
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        return render_template('panel.html')
    elif user_role == 'cliente':
        return redirect(url_for('listar_productos'))
    else:
        abort(403)

@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    user_role = session.get('user_role')
    if user_role in ('farmacia', 'cliente'):
        user_id = session.get('user_id')
        user_info = get_user_info(user_id)
        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            direccion = request.form['direccion']
            provincia = request.form['provincia']
            localidad = request.form['localidad']
            numero_telefono = request.form['numero_telefono']
            correo_electronico = request.form['correo_electronico']
            nombre_usuario = request.form['nombre_usuario']
            contraseña = request.form['contraseña']
            logo_url= request.form['logo_url']
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('UPDATE usuarios SET nombre=?, apellido=?, direccion=?, provincia=?, localidad=?, numero_telefono=?, correo_electronico=?, contraseña=?, nombre_usuario=?, logo_url=? WHERE id=?',
                            (nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, contraseña, nombre_usuario, logo_url, user_id))
                db.commit()
            return redirect(url_for('perfil'))
        else:
            if user_info:
                nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, contraseña, logo_url = user_info
            else:
                nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, contraseña, logo_url = "", "", "", "", "", "", "", "", "", ""
            return render_template('editar_perfil.html', nombre=nombre, apellido=apellido, direccion=direccion, provincia=provincia, localidad=localidad, numero_telefono=numero_telefono, correo_electronico=correo_electronico, nombre_usuario=nombre_usuario, contraseña=contraseña, logo_url=logo_url)
    else:
        abort(403)

@app.route('/eliminar_cuenta', methods=['POST'])
def eliminar_cuenta():
    user_id = session.get('user_id')
    if user_id:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('DELETE FROM usuarios WHERE id=?', (user_id,))
            db.commit()
        session.clear()
        return redirect(url_for('login'))
    else:
        abort(403)

@app.route('/productos/agregar', methods=['GET', 'POST'])
def agregar_producto():
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        if request.method == 'POST':
            nombre = request.form['nombre']
            imagen = request.form['imagen']
            descripcion = request.form['descripcion']
            cantidad = int(request.form['cantidad'])
            precio_unitario = float(request.form['precio_unitario'])
            id_categoria = int(request.form['categoria'])
            id_farmacia = session.get('user_id')
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('INSERT INTO productos (nombre, imagen, descripcion, cantidad, precio_unitario, id_categoria, id_farmacia) VALUES (?, ?, ?, ?, ?, ?, ?)', (nombre, imagen, descripcion, cantidad, precio_unitario, id_categoria, id_farmacia))
                product_id = cursor.lastrowid
                db.commit()
                cursor.execute('INSERT INTO farmacia_productos (id_usuario, id_producto) VALUES (?, ?)', (id_farmacia, product_id))
                db.commit()
            return redirect(url_for('farmacia_inventario'))
        else:
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('SELECT id, nombre FROM categorias')
                categorias = cursor.fetchall()
            return render_template('agregar_producto.html', categorias=categorias)
    else:
        abort(403)

@app.route('/productos/editar/<int:id_producto>', methods=['GET', 'POST'])
def editar_producto(id_producto):
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?', (id_producto,))
            product_owner = cursor.fetchone()
            if not product_owner or product_owner[0] != session.get('user_id'):
                abort(403)
        if request.method == 'POST':
            nombre = request.form['nombre']
            imagen=request.form['imagen']
            descripcion = request.form['descripcion']
            precio_unitario = float(request.form['precio_unitario'])
            cantidad = int(request.form['cantidad'])
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('UPDATE productos SET nombre=?, imagen=?,descripcion=?, precio_unitario=?, cantidad=? WHERE id=?',
                            (nombre, imagen,descripcion, precio_unitario, cantidad, id_producto))
                db.commit()
            return redirect(url_for('dashboard'))
        else:
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('SELECT nombre, imagen,descripcion, precio_unitario, cantidad FROM productos WHERE id=?',
                            (id_producto,))
                producto = cursor.fetchone()
            if producto:
                return render_template('editar_producto.html', producto=producto)
            else:
                abort(404) 
    else:
        abort(403)

@app.route('/productos/eliminar/<int:id_producto>', methods=['POST'])
def eliminar_producto(id_producto):
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?', (id_producto,))
            product_owner = cursor.fetchone()
            if not product_owner or product_owner[0] != session.get('user_id'):
                abort(403)
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('DELETE FROM productos WHERE id=?', (id_producto,))
            cursor.execute('DELETE FROM farmacia_productos WHERE id_producto=?', (id_producto,))
            db.commit()
        return redirect(url_for('farmacia_inventario'))
    else:
        abort(403)

@app.route('/agregar_al_carrito/<int:id_producto>', methods=['POST'])
def agregar_al_carrito(id_producto):
    user_id = session.get('user_id')
    if user_id:
        cantidad = int(request.form['cantidad'])
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM productos WHERE id=?', (id_producto,))
            producto = cursor.fetchone()
            if producto:
                cursor.execute('SELECT * FROM carritos WHERE id_usuario=? AND estado="abierto"', (user_id,))
                carrito = cursor.fetchone()
                if not carrito:
                    cursor.execute('INSERT INTO carritos (id_usuario, fecha, estado, total) VALUES (?, ?, ?, ?)', (user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "abierto", 0))
                    db.commit()
                    carrito = cursor.execute('SELECT * FROM carritos WHERE id_usuario=? AND estado="abierto"', (user_id,)).fetchone()
                    carrito_id = carrito[0]
                else:
                    carrito_id = carrito[0]
                new_total = carrito[4] + (producto[5] * cantidad)
                cursor.execute('UPDATE carritos SET total=? WHERE id=?', (new_total, carrito_id))
                db.commit()
                cursor.execute('INSERT OR REPLACE INTO detalles_carrito (id_carrito, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)', (carrito_id, id_producto, cantidad, producto[5]))
                db.commit()
                return redirect(url_for('ver_detalle_producto', id_producto=id_producto))
            else:
                abort(404)
    else:
        abort(403)

@app.route('/eliminar_del_carrito/<int:id_detalle_carrito>', methods=['POST'])
def eliminar_del_carrito(id_detalle_carrito):
    user_id = session.get('user_id')
    if user_id:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('DELETE FROM detalles_carrito WHERE id = ? AND id_carrito IN (SELECT id FROM carritos WHERE id_usuario = ? AND estado = "abierto")', (id_detalle_carrito, user_id))
            db.commit()
            return redirect(url_for('ver_carrito'))
    else:
        abort(403)

@app.route('/carrito', methods=['GET'])
def ver_carrito():
    user_id = session.get('user_id')
    if user_id:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM carritos WHERE id_usuario=? AND estado="abierto"', (user_id,))
            carrito = cursor.fetchone()
            if carrito:
                cursor.execute('SELECT dc.id, p.id, p.nombre, p.precio_unitario, dc.cantidad FROM detalles_carrito dc JOIN productos p ON dc.id_producto = p.id JOIN carritos c ON dc.id_carrito = c.id WHERE c.id_usuario = ? AND c.estado = "abierto"', (user_id,))
                carrito = cursor.fetchall()
                total_carrito = 0
                total_carrito = sum(detalle[3] * detalle[4] for detalle in carrito)
                return render_template('carrito.html', carrito=carrito, total_carrito=total_carrito)
            else:
                return redirect(url_for('listar_productos'))
    else:
        abort(403)

@app.route('/carrito/comprar', methods=['POST'])
def comprar_carrito():
    user_id = session.get('user_id')
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM carritos WHERE id_usuario = ?', (user_id,))
        carrito = cursor.fetchone()
        if carrito:
            cursor.execute('SELECT dc.id, p.nombre, dc.precio_unitario, dc.cantidad FROM detalles_carrito dc INNER JOIN productos p ON dc.id_producto = p.id WHERE dc.id_carrito = ?', (carrito[0],))
            detalles_carrito = cursor.fetchall()
            if detalles_carrito:
                total = sum(detalle[2] * detalle[3] for detalle in detalles_carrito)
                descripcion_productos = "\n".join(f"{detalle[1]} (Precio unitario: ${detalle[2]:.2f}, Cantidad: {detalle[3]}) | " for detalle in detalles_carrito)
                link_pago = crear_enlace_de_pago(descripcion_productos, total)
                db.commit()
                return render_template('carrito_pago.html', link_pago=link_pago)
    return redirect(url_for('ver_carrito'))

@app.route('/pago_exitoso', methods=['GET'])
def pago_exitoso():
    payment_status = request.args.get('status')
    collection_status = request.args.get('collection_status')
    preference_id = request.args.get('preference_id')
    site_id = request.args.get('site_id')
    external_reference = request.args.get('external_reference')
    merchant_order_id = request.args.get('merchant_order_id')
    collection_id = request.args.get('collection_id')
    payment_id = request.args.get('payment_id')
    payment_type = request.args.get('payment_type')
    processing_mode = request.args.get('processing_mode')
    if payment_status == 'approved' and collection_status == 'approved':
        user_id = session.get('user_id')
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM carritos WHERE id_usuario = ?', (user_id,))
            carrito = cursor.fetchone()
            if carrito:
                cursor.execute('SELECT * FROM detalles_carrito WHERE id_carrito = ?', (carrito[0],))
                detalles_carrito = cursor.fetchall()
                if detalles_carrito:
                    total = sum(detalle[3] * detalle[4] for detalle in detalles_carrito)
                    cursor.execute('SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?', (detalles_carrito[0][2],))
                    id_vendedor = cursor.fetchone()[0]
                    cursor.execute('INSERT INTO ventas (id_vendedor, id_comprador, fecha, total) VALUES (?, ?, ?, ?)', (id_vendedor, user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), total))
                    venta_id = cursor.lastrowid
                    for detalle in detalles_carrito:
                        cursor.execute('INSERT INTO detalles_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)', (venta_id, detalle[2], detalle[3], detalle[4]))
                        cursor.execute('UPDATE productos SET cantidad = cantidad - ? WHERE id = ?', (detalle[3], detalle[2]))
                    cursor.execute('DELETE FROM detalles_carrito WHERE id_carrito = ?', (carrito[0],))
                    cursor.execute('DELETE FROM carritos WHERE id = ?', (carrito[0],))
                    db.commit()
                    success = "Pago exitoso. Gracias por tu compra."
                    return render_template('carrito.html', success=success)
    else:
        error = "Pago fallido o pendiente. Por favor, intenta nuevamente."
        return render_template('carrito.html', error=error)
    error = "Error en la respuesta de pago."
    return render_template('carrito.html', error=error)              

@app.route('/ventas')
def ventas():
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        farmacia_id = session.get('user_id')
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT v.id, v.fecha, v.total, u.nombre AS comprador_nombre, u.correo_electronico AS comprador_correo FROM ventas v INNER JOIN usuarios u ON v.id_comprador = u.id WHERE v.id_vendedor = ?', (farmacia_id,))
            ventas = cursor.fetchall()
        return render_template('ventas.html', ventas=ventas)
    else:
        abort(403)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host="0.0.0.0")