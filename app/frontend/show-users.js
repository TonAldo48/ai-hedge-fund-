const postgres = require('postgres');
require('dotenv').config({ path: '.env.local' });

const sql = postgres(process.env.POSTGRES_URL);

(async () => {
  try {
    const users = await sql`SELECT id, email FROM "User" ORDER BY email`;
    console.log('📊 Users in your database:');
    console.log('=========================');
    users.forEach(user => {
      const userType = user.email.startsWith('guest-') ? '👤 Guest' : '👨‍💼 Regular';
      console.log(`${userType}: ${user.email}`);
      console.log(`   ID: ${user.id}`);
      console.log('');
    });
    console.log(`Total users: ${users.length}`);
    process.exit(0);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
})(); 