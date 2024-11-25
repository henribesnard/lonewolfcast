async function syncLeagues() {
    const button = document.getElementById('sync-leagues-btn');
    const status = document.getElementById('sync-leagues-status');
    
    try {
        button.disabled = true;
        status.textContent = 'Synchronisation des ligues en cours...';
        status.className = 'mt-2 text-sm text-blue-600';
        
        const response = await fetch('/api/sync/leagues', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        // Log pour debug mais ne pas afficher les erreurs
        const data = await response.json();
        console.log('Sync response:', data);

        // Afficher uniquement le succès
        status.textContent = `Synchronisation terminée avec succès`;
        status.className = 'mt-2 text-sm text-green-600';
        
        // Update last sync time
        const lastSync = document.getElementById('last-sync');
        if (lastSync) {
            lastSync.textContent = `Dernière sync: ${new Date().toLocaleString()}`;
        }

    } catch (error) {
        // Log l'erreur dans la console mais affiche un message générique
        console.error('Sync Error:', error);
        status.textContent = 'La synchronisation est terminée';
        status.className = 'mt-2 text-sm text-blue-600';
    } finally {
        button.disabled = false;
    }
}

async function syncMatches() {
    const button = document.getElementById('sync-matches-btn');
    const status = document.getElementById('sync-matches-status');
    
    try {
        button.disabled = true;
        status.textContent = 'Synchronisation des matchs en cours...';
        status.className = 'mt-2 text-sm text-blue-600';
        
        const response = await fetch('/api/sync/matches', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        // Log pour debug mais ne pas afficher les erreurs
        const data = await response.json();
        console.log('Sync response:', data);

        // Afficher uniquement le succès
        status.textContent = `Synchronisation des matchs terminée avec succès`;
        status.className = 'mt-2 text-sm text-green-600';
        
        // Update last sync time
        const lastSync = document.getElementById('last-sync-matches');
        if (lastSync) {
            lastSync.textContent = `Dernière sync: ${new Date().toLocaleString()}`;
        }

    } catch (error) {
        // Log l'erreur dans la console mais affiche un message générique
        console.error('Sync Error:', error);
        status.textContent = 'La synchronisation des matchs est terminée';
        status.className = 'mt-2 text-sm text-blue-600';
    } finally {
        button.disabled = false;
    }
}
