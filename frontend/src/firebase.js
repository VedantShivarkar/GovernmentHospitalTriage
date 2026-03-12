import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

// REPLACE THIS OBJECT WITH THE ONE FROM YOUR FIREBASE CONSOLE
const firebaseConfig = {
  apiKey: "AIzaSyBA3xeAkwvsIXIcFxoJcBuqKtJ2SqVeK48",
  authDomain: "govthospitaltriage.firebaseapp.com",
  projectId: "govthospitaltriage",
  storageBucket: "govthospitaltriage.firebasestorage.app",
  messagingSenderId: "197857121701",
  appId: "1:197857121701:web:26eb809e15f09ed68c444c",
  measurementId: "G-L4W032LYGB"
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);