const fakeUsers = [
  {
    name: 'Alex Johnson',
    email: 'alex.johnson@example.com',
    phone: '(555) 123-4567',
    address: '742 Evergreen Terrace, Springfield, IL 62704',
  },
  {
    name: 'Maria Garcia',
    email: 'maria.garcia@example.com',
    phone: '(555) 234-5678',
    address: '1600 Pennsylvania Ave, Washington, DC 20500',
  },
  {
    name: 'James Chen',
    email: 'james.chen@example.com',
    phone: '(555) 345-6789',
    address: '350 Fifth Avenue, New York, NY 10118',
  },
  {
    name: 'Sarah Williams',
    email: 'sarah.williams@example.com',
    phone: '(555) 456-7890',
    address: '221B Baker Street, London, CA 90210',
  },
  {
    name: 'David Kim',
    email: 'david.kim@example.com',
    phone: '(555) 567-8901',
    address: '1 Infinite Loop, Cupertino, CA 95014',
  },
  {
    name: 'Emily Brown',
    email: 'emily.brown@example.com',
    phone: '(555) 678-9012',
    address: '4059 Mt Lee Dr, Los Angeles, CA 90068',
  },
  {
    name: 'Carlos Rivera',
    email: 'carlos.rivera@example.com',
    phone: '(555) 789-0123',
    address: '100 Universal City Plaza, Universal City, CA 91608',
  },
  {
    name: 'Priya Patel',
    email: 'priya.patel@example.com',
    phone: '(555) 890-1234',
    address: '1 Hacker Way, Menlo Park, CA 94025',
  },
];

export function getRandomUser() {
  const index = Math.floor(Math.random() * fakeUsers.length);
  return { ...fakeUsers[index] };
}

export default fakeUsers;
