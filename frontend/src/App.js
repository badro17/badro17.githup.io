import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [cart, setCart] = useState([]);
  const [showCart, setShowCart] = useState(false);
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [showChatModal, setShowChatModal] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Fetch products and categories
  useEffect(() => {
    fetchProducts();
    fetchCategories();
    fetchConversations();
  }, []);

  // Filter products based on category and search
  useEffect(() => {
    let filtered = products;
    
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(product => product.category === selectedCategory);
    }
    
    if (searchTerm) {
      filtered = filtered.filter(product => 
        product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    setFilteredProducts(filtered);
  }, [products, selectedCategory, searchTerm]);

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products`);
      const data = await response.json();
      setProducts(data.products);
      setFilteredProducts(data.products);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/categories`);
      const data = await response.json();
      setCategories(data.categories);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchConversations = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/conversations`);
      const data = await response.json();
      setConversations(data.conversations);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
      setCart(cart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
    } else {
      setCart(cart.map(item => 
        item.id === productId 
          ? { ...item, quantity: quantity }
          : item
      ));
    }
  };

  const getTotalAmount = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const OrderForm = () => {
    const [formData, setFormData] = useState({
      customer_name: '',
      customer_phone: '',
      customer_address: '',
      notes: ''
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        const orderData = {
          ...formData,
          items: cart.map(item => ({
            product_id: item.id,
            product_name: item.name,
            quantity: item.quantity,
            price: item.price
          })),
          total_amount: getTotalAmount()
        };

        const response = await fetch(`${BACKEND_URL}/api/orders`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(orderData),
        });

        if (response.ok) {
          alert('Commande passée avec succès !');
          setCart([]);
          setShowOrderForm(false);
          setShowCart(false);
        }
      } catch (error) {
        console.error('Error placing order:', error);
        alert('Erreur lors de la commande');
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-8 rounded-lg max-w-md w-full mx-4 max-h-96 overflow-y-auto">
          <h3 className="text-xl font-bold mb-4 text-blue-800">Informations de Commande</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Nom complet"
              value={formData.customer_name}
              onChange={(e) => setFormData({...formData, customer_name: e.target.value})}
              className="w-full p-3 border rounded-lg"
              required
            />
            <input
              type="tel"
              placeholder="Numéro de téléphone"
              value={formData.customer_phone}
              onChange={(e) => setFormData({...formData, customer_phone: e.target.value})}
              className="w-full p-3 border rounded-lg"
              required
            />
            <textarea
              placeholder="Adresse complète"
              value={formData.customer_address}
              onChange={(e) => setFormData({...formData, customer_address: e.target.value})}
              className="w-full p-3 border rounded-lg h-20"
              required
            />
            <textarea
              placeholder="Notes supplémentaires (optionnel)"
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              className="w-full p-3 border rounded-lg h-16"
            />
            <div className="flex space-x-4">
              <button
                type="submit"
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
              >
                Confirmer Commande
              </button>
              <button
                type="button"
                onClick={() => setShowOrderForm(false)}
                className="flex-1 bg-gray-400 text-white py-3 rounded-lg hover:bg-gray-500"
              >
                Annuler
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const ChatModal = () => {
    const [chatData, setChatData] = useState({
      customer_name: '',
      customer_phone: '',
      message: ''
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        const response = await fetch(`${BACKEND_URL}/api/conversations`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(chatData),
        });

        if (response.ok) {
          alert('Message envoyé avec succès !');
          setChatData({ customer_name: '', customer_phone: '', message: '' });
          setShowChatModal(false);
          fetchConversations();
        }
      } catch (error) {
        console.error('Error sending message:', error);
        alert('Erreur lors de l\'envoi du message');
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-8 rounded-lg max-w-md w-full mx-4">
          <h3 className="text-xl font-bold mb-4 text-blue-800">Contactez-nous</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Votre nom"
              value={chatData.customer_name}
              onChange={(e) => setChatData({...chatData, customer_name: e.target.value})}
              className="w-full p-3 border rounded-lg"
              required
            />
            <input
              type="tel"
              placeholder="Votre téléphone"
              value={chatData.customer_phone}
              onChange={(e) => setChatData({...chatData, customer_phone: e.target.value})}
              className="w-full p-3 border rounded-lg"
              required
            />
            <textarea
              placeholder="Votre message ou question"
              value={chatData.message}
              onChange={(e) => setChatData({...chatData, message: e.target.value})}
              className="w-full p-3 border rounded-lg h-24"
              required
            />
            <div className="flex space-x-4">
              <button
                type="submit"
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
              >
                Envoyer Message
              </button>
              <button
                type="button"
                onClick={() => setShowChatModal(false)}
                className="flex-1 bg-gray-400 text-white py-3 rounded-lg hover:bg-gray-500"
              >
                Fermer
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-lg sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xl">PS</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-blue-800">Pharmacie Saidani</h1>
                <p className="text-sm text-gray-600">rue Ali Bouhaja Birtouta, Algérie</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowChatModal(true)}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2"
              >
                <span>💬</span>
                <span>Contact</span>
              </button>
              <button
                onClick={() => setShowCart(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
              >
                <span>🛒</span>
                <span>Panier ({cart.length})</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-4">Votre Pharmacie de Confiance</h2>
          <p className="text-xl mb-8">Produits pharmaceutiques et cosmétiques de qualité</p>
          <div className="flex justify-center">
            <img 
              src="https://images.unsplash.com/photo-1638202993928-7267aad84c31" 
              alt="Pharmacie professionnelle" 
              className="w-64 h-48 object-cover rounded-lg shadow-lg"
            />
          </div>
        </div>
      </section>

      {/* Search and Filter */}
      <section className="bg-white py-8 shadow-sm">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
            <input
              type="text"
              placeholder="Rechercher un produit..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 p-3 border rounded-lg"
            />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="p-3 border rounded-lg"
            >
              <option value="all">Toutes les catégories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
        </div>
      </section>

      {/* Products Section */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-8 text-blue-800">Nos Produits</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredProducts.map(product => (
              <div key={product.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                <img 
                  src={product.image_url} 
                  alt={product.name}
                  className="w-full h-48 object-cover"
                />
                <div className="p-6">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-semibold text-gray-800">{product.name}</h3>
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
                      {product.category}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-4">{product.description}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-2xl font-bold text-blue-600">
                      {product.price.toFixed(2)} DA
                    </span>
                    <button
                      onClick={() => addToCart(product)}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Ajouter au panier
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Cart Modal */}
      {showCart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-8 rounded-lg max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
            <h3 className="text-xl font-bold mb-4 text-blue-800">Votre Panier</h3>
            {cart.length === 0 ? (
              <p className="text-gray-600">Votre panier est vide</p>
            ) : (
              <>
                {cart.map(item => (
                  <div key={item.id} className="flex items-center justify-between py-4 border-b">
                    <div className="flex-1">
                      <h4 className="font-semibold">{item.name}</h4>
                      <p className="text-gray-600">{item.price.toFixed(2)} DA</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        className="bg-gray-200 px-2 py-1 rounded"
                      >
                        -
                      </button>
                      <span className="px-3">{item.quantity}</span>
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        className="bg-gray-200 px-2 py-1 rounded"
                      >
                        +
                      </button>
                      <button
                        onClick={() => removeFromCart(item.id)}
                        className="bg-red-500 text-white px-2 py-1 rounded ml-2"
                      >
                        Supprimer
                      </button>
                    </div>
                  </div>
                ))}
                <div className="mt-4 pt-4 border-t">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-xl font-bold">Total: {getTotalAmount().toFixed(2)} DA</span>
                  </div>
                  <div className="flex space-x-4">
                    <button
                      onClick={() => setShowOrderForm(true)}
                      className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
                    >
                      Passer Commande
                    </button>
                    <button
                      onClick={() => setShowCart(false)}
                      className="flex-1 bg-gray-400 text-white py-3 rounded-lg hover:bg-gray-500"
                    >
                      Continuer Shopping
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Order Form Modal */}
      {showOrderForm && <OrderForm />}

      {/* Chat Modal */}
      {showChatModal && <ChatModal />}

      {/* Footer */}
      <footer className="bg-blue-800 text-white py-8">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">Pharmacie Saidani</h3>
              <p className="mb-2">📍 rue Ali Bouhaja Birtouta, Algérie</p>
              <p className="mb-2">📞 Appelez-nous pour plus d'informations</p>
              <p>✉️ Contactez-nous via notre formulaire</p>
            </div>
            <div>
              <h3 className="text-xl font-bold mb-4">Nos Services</h3>
              <ul className="space-y-2">
                <li>• Médicaments sur ordonnance</li>
                <li>• Produits cosmétiques</li>
                <li>• Compléments alimentaires</li>
                <li>• Conseils pharmaceutiques</li>
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-bold mb-4">Horaires</h3>
              <p className="mb-2">Lundi - Vendredi: 8h00 - 19h00</p>
              <p className="mb-2">Samedi: 8h00 - 17h00</p>
              <p>Dimanche: 9h00 - 13h00</p>
            </div>
          </div>
          <div className="border-t border-blue-700 mt-8 pt-4 text-center">
            <p>&copy; 2025 Pharmacie Saidani. Tous droits réservés.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;