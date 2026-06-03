"""
AI MODULE 1: Geographic Shipment Clustering
Uses KMeans to cluster shipments by geographic location
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt
import seaborn as sns
import json
import warnings
warnings.filterwarnings('ignore')


class ShipmentClusterer:
    """Geographic clustering of shipments using KMeans"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.optimal_k = None
        self.model = None
        self.scaler = StandardScaler()
        self.cluster_labels = None
        self.metrics = {}
        
    def find_optimal_clusters(self, max_k: int = 15, min_k: int = 2) -> int:
        """
        Use Elbow Method to find optimal number of clusters
        """
        print("Finding optimal number of clusters...")
        print("="*80)
        
        # Prepare data - use routes for clustering
        if 'origin_city' in self.data.columns and 'destination_city' in self.data.columns:
            # Create location pairs
            location_features = self.data[['origin_city', 'destination_city']].copy()
            # Simple numeric encoding for demo - in production use proper geocoding
            location_features['origin_hash'] = location_features['origin_city'].astype(str).apply(hash) % 10000
            location_features['dest_hash'] = location_features['destination_city'].astype(str).apply(hash) % 10000
            X = location_features[['origin_hash', 'dest_hash']].values
        elif 'latitude' in self.data.columns and 'longitude' in self.data.columns:
            X = self.data[['latitude', 'longitude']].values
        else:
            # Fallback: use distance and weight
            features = []
            if 'distance_miles' in self.data.columns:
                features.append('distance_miles')
            if 'weight' in self.data.columns:
                features.append('weight')
            if not features:
                print("Warning: No suitable clustering features found")
                return 3
            X = self.data[features].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Calculate metrics for different k values
        inertias = []
        silhouette_scores = []
        k_range = range(min_k, max_k + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            inertias.append(kmeans.inertia_)
            
            if k < len(X):
                sil_score = silhouette_score(X_scaled, labels)
                silhouette_scores.append(sil_score)
            else:
                silhouette_scores.append(0)
            
            print(f"K={k}: Inertia={kmeans.inertia_:.2f}, Silhouette={silhouette_scores[-1]:.3f}")
        
        # Find elbow using rate of change
        inertia_diff = np.diff(inertias)
        inertia_diff_2 = np.diff(inertia_diff)
        elbow_idx = np.argmax(inertia_diff_2) + min_k
        
        # Also consider best silhouette score
        best_sil_idx = np.argmax(silhouette_scores) + min_k
        
        # Choose optimal k (prefer silhouette if difference is significant)
        if silhouette_scores[best_sil_idx - min_k] > silhouette_scores[elbow_idx - min_k] * 1.1:
            self.optimal_k = best_sil_idx
        else:
            self.optimal_k = elbow_idx
        
        print(f"\n✓ Optimal K determined: {self.optimal_k}")
        print(f"  Elbow method suggested: {elbow_idx}")
        print(f"  Best silhouette at: {best_sil_idx}")
        
        return self.optimal_k
    
    def fit_clustering(self, n_clusters: int = None):
        """
        Fit KMeans clustering model
        """
        if n_clusters is None:
            if self.optimal_k is None:
                n_clusters = self.find_optimal_clusters()
            else:
                n_clusters = self.optimal_k
        
        print(f"\nFitting KMeans with {n_clusters} clusters...")
        
        # Prepare features
        if 'origin_city' in self.data.columns and 'destination_city' in self.data.columns:
            location_features = self.data[['origin_city', 'destination_city']].copy()
            location_features['origin_hash'] = location_features['origin_city'].astype(str).apply(hash) % 10000
            location_features['dest_hash'] = location_features['destination_city'].astype(str).apply(hash) % 10000
            X = location_features[['origin_hash', 'dest_hash']].values
        elif 'latitude' in self.data.columns and 'longitude' in self.data.columns:
            X = self.data[['latitude', 'longitude']].values
        else:
            features = []
            if 'distance_miles' in self.data.columns:
                features.append('distance_miles')
            if 'weight' in self.data.columns:
                features.append('weight')
            X = self.data[features].values
        
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit model
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.cluster_labels = self.model.fit_predict(X_scaled)
        
        # Calculate metrics
        self.metrics = {
            'n_clusters': n_clusters,
            'inertia': float(self.model.inertia_),
            'silhouette_score': float(silhouette_score(X_scaled, self.cluster_labels)),
            'davies_bouldin_score': float(davies_bouldin_score(X_scaled, self.cluster_labels))
        }
        
        # Add cluster statistics
        cluster_sizes = pd.Series(self.cluster_labels).value_counts().sort_index()
        self.metrics['cluster_sizes'] = cluster_sizes.to_dict()
        self.metrics['avg_cluster_size'] = float(cluster_sizes.mean())
        self.metrics['min_cluster_size'] = int(cluster_sizes.min())
        self.metrics['max_cluster_size'] = int(cluster_sizes.max())
        
        print(f"✓ Clustering complete")
        print(f"  Silhouette Score: {self.metrics['silhouette_score']:.3f}")
        print(f"  Davies-Bouldin Score: {self.metrics['davies_bouldin_score']:.3f}")
        print(f"  Avg Cluster Size: {self.metrics['avg_cluster_size']:.1f}")
        
        return self.cluster_labels
    
    def get_clustered_data(self) -> pd.DataFrame:
        """
        Return data with cluster assignments
        """
        data_clustered = self.data.copy()
        data_clustered['cluster_id'] = self.cluster_labels
        return data_clustered
    
    def analyze_clusters(self) -> dict:
        """
        Analyze cluster characteristics
        """
        data_clustered = self.get_clustered_data()
        
        cluster_analysis = {}
        
        for cluster_id in range(self.metrics['n_clusters']):
            cluster_data = data_clustered[data_clustered['cluster_id'] == cluster_id]
            
            analysis = {
                'size': len(cluster_data),
                'percentage': (len(cluster_data) / len(data_clustered)) * 100
            }
            
            # Numeric features analysis
            numeric_cols = ['distance_miles', 'weight', 'revenue', 'fuel_gallons']
            for col in numeric_cols:
                if col in cluster_data.columns:
                    analysis[f'{col}_mean'] = float(cluster_data[col].mean())
                    analysis[f'{col}_sum'] = float(cluster_data[col].sum())
            
            # Top routes
            if 'origin_city' in cluster_data.columns and 'destination_city' in cluster_data.columns:
                top_routes = cluster_data.groupby(['origin_city', 'destination_city']).size().sort_values(ascending=False).head(5)
                analysis['top_routes'] = {f"{k[0]}-{k[1]}": int(v) for k, v in top_routes.items()}
            
            cluster_analysis[f'cluster_{cluster_id}'] = analysis
        
        return cluster_analysis
    
    def save_results(self, output_dir: str = "optimization/results"):
        """
        Save clustering results
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save clustered data
        clustered_data = self.get_clustered_data()
        clustered_data.to_csv(f"{output_dir}/shipments_clustered.csv", index=False)
        
        # Save metrics
        with open(f"{output_dir}/clustering_metrics.json", 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        # Save cluster analysis
        cluster_analysis = self.analyze_clusters()
        with open(f"{output_dir}/cluster_analysis.json", 'w') as f:
            json.dump(cluster_analysis, f, indent=2)
        
        print(f"\n✓ Clustering results saved to {output_dir}/")
        
        return clustered_data


def run_clustering(data_path: str = "processed_data/unified_logistics_dataset.csv"):
    """
    Main function to run geographic clustering
    """
    print("="*80)
    print("AI MODULE 1: GEOGRAPHIC SHIPMENT CLUSTERING")
    print("="*80)
    
    # Load data
    print("\nLoading data...")
    data = pd.read_csv(data_path)
    print(f"✓ Loaded {len(data):,} shipments")
    
    # Initialize clusterer
    clusterer = ShipmentClusterer(data)
    
    # Find optimal clusters
    optimal_k = clusterer.find_optimal_clusters()
    
    # Fit clustering
    clusterer.fit_clustering(optimal_k)
    
    # Analyze clusters
    print("\n" + "="*80)
    print("CLUSTER ANALYSIS")
    print("="*80)
    cluster_analysis = clusterer.analyze_clusters()
    for cluster_name, analysis in cluster_analysis.items():
        print(f"\n{cluster_name.upper()}:")
        print(f"  Size: {analysis['size']:,} shipments ({analysis['percentage']:.1f}%)")
        if 'distance_miles_mean' in analysis:
            print(f"  Avg Distance: {analysis['distance_miles_mean']:.1f} miles")
        if 'weight_mean' in analysis:
            print(f"  Avg Weight: {analysis['weight_mean']:.1f} lbs")
        if 'revenue_sum' in analysis:
            print(f"  Total Revenue: ${analysis['revenue_sum']:,.2f}")
    
    # Save results
    clustered_data = clusterer.save_results()
    
    print("\n✓ Clustering module complete!")
    
    return clustered_data, clusterer


if __name__ == "__main__":
    run_clustering()
